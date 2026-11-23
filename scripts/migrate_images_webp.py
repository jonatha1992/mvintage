#!/usr/bin/env python3
"""Migra imágenes de productos existentes a WebP 800px (calidad 80) conservando los originales.

Uso:
  python scripts/migrate_images_webp.py                     # dry-run (por defecto)
  python scripts/migrate_images_webp.py --product-id 10     # dry-run de 1 producto
  python scripts/migrate_images_webp.py --product-id 10 --apply
  python scripts/migrate_images_webp.py --apply             # migra todas las pendientes
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import os
import pathlib
import subprocess
import sys
import urllib.request
from typing import Any

from PIL import Image, ImageOps

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_API_URL = 'https://showroomisabella-api.tecnofusion.dev/api/v1/products/'
DEFAULT_ENV_FILE = REPO_ROOT / 'frontend' / '.env.test'
DEFAULT_BACKUP_DIR = REPO_ROOT / 'backups-imagenes'


def load_env_file(path: pathlib.Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def fetch_products(api_url: str) -> list[dict[str, Any]]:
    req = urllib.request.Request(api_url, headers={'User-Agent': 'showroomisabella-migrator/1.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


def download_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': 'showroomisabella-migrator/1.0'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def convert_to_webp(raw: bytes, max_width: int, quality: int) -> tuple[bytes, tuple[int, int], tuple[int, int]]:
    with Image.open(io.BytesIO(raw)) as img:
        img = ImageOps.exif_transpose(img)
        orig_size = img.size
        if img.width > max_width:
            new_height = round(img.height * (max_width / img.width))
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')
        elif img.mode == 'RGBA':
            bg = Image.new('RGB', img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[-1])
            img = bg
        out = io.BytesIO()
        img.save(out, format='WEBP', quality=quality, method=6)
        return out.getvalue(), orig_size, img.size


def upload_webp(img_server_url: str, api_key: str, data: bytes, filename: str) -> str:
    boundary = '----ShowroomIsabellaWebpBoundary7MA4YWxkTrZu0gW'
    body = io.BytesIO()
    body.write(f'--{boundary}\r\n'.encode())
    body.write(b'Content-Disposition: form-data; name="folder"\r\n\r\nproductos\r\n')
    body.write(f'--{boundary}\r\n'.encode())
    body.write(
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
    )
    body.write(b'Content-Type: image/webp\r\n\r\n')
    body.write(data)
    body.write(f'\r\n--{boundary}--\r\n'.encode())

    req = urllib.request.Request(
        f'{img_server_url.rstrip("/")}/v1/showroomisabella/upload',
        data=body.getvalue(),
        method='POST',
        headers={
            'X-API-Key': api_key,
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'User-Agent': 'showroomisabella-migrator/1.0',
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read().decode('utf-8'))
    return payload['secure_url']


def verify_url_ok(url: str) -> int:
    req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'showroomisabella-migrator/1.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status


def update_db_image_url(
    image_id: int, new_url: str, ssh_host: str, db_container: str, db_user: str, db_name: str
) -> None:
    safe_url = new_url.replace("'", "''")
    sql = f"UPDATE productimage SET image_url = '{safe_url}' WHERE id = {int(image_id)};"
    cmd = [
        'ssh',
        ssh_host,
        f'docker exec {db_container} psql -U {db_user} -d {db_name} -v ON_ERROR_STOP=1 -c "{sql}"',
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        raise RuntimeError(f'Error actualizando DB image_id={image_id}: {res.stderr.strip()}')
    if 'UPDATE 1' not in res.stdout:
        raise RuntimeError(f'Respuesta inesperada en DB image_id={image_id}: {res.stdout.strip()}')


def build_400_variant(url: str) -> str:
    return url.replace('/image/upload/', '/image/upload/w_400,q_80,f_webp/', 1)


def main() -> int:
    parser = argparse.ArgumentParser(description='Migrar imágenes de productos a WebP 800px.')
    parser.add_argument('--apply', action='store_true', help='Aplicar subida y actualización en DB (por defecto dry-run).')
    parser.add_argument('--dry-run', action='store_true', help='Simular sin modificar nada (por defecto).')
    parser.add_argument('--product-id', type=int, default=None, help='Procesar solo un product_id.')
    parser.add_argument('--max-width', type=int, default=800, help='Ancho máximo en px (default: 800).')
    parser.add_argument('--quality', type=int, default=80, help='Calidad WebP (default: 80).')
    parser.add_argument('--force', action='store_true', help='Reprocesar incluso imágenes que ya son .webp.')
    parser.add_argument('--api-url', default=DEFAULT_API_URL)
    parser.add_argument('--env-file', type=pathlib.Path, default=DEFAULT_ENV_FILE)
    parser.add_argument('--backup-dir', type=pathlib.Path, default=DEFAULT_BACKUP_DIR)
    parser.add_argument('--ssh-host', default='server')
    parser.add_argument('--db-container', default='showroomisabella-db')
    parser.add_argument('--db-user', default='showroom')
    parser.add_argument('--db-name', default='showroomisabella')
    args = parser.parse_args()

    apply_mode = bool(args.apply and not args.dry_run)
    env = load_env_file(args.env_file)
    img_server_url = os.environ.get('VITE_IMG_SERVER_URL') or env.get('VITE_IMG_SERVER_URL', 'https://img.tecnofusion.dev')
    img_api_key = os.environ.get('VITE_IMG_API_KEY') or env.get('VITE_IMG_API_KEY', '')

    if apply_mode and not img_api_key:
        print('ERROR: Falta VITE_IMG_API_KEY para ejecutar con --apply.', file=sys.stderr)
        return 1

    products = fetch_products(args.api_url)
    all_images = [
        {
            'product_id': p['id'],
            'product_name': p['name'],
            'image_id': img['id'],
            'original_url': img['image_url'],
        }
        for p in products
        for img in p.get('images', [])
    ]

    args.backup_dir.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    backup_path = args.backup_dir / f'{today}.json'
    if not backup_path.exists():
        backup_path.write_text(json.dumps(all_images, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f'Backup JSON guardado en: {backup_path}')
    else:
        print(f'Backup JSON ya existente (conservado): {backup_path}')

    targets = [x for x in all_images if args.product_id is None or x['product_id'] == args.product_id]
    if not targets:
        print('No se encontraron imágenes para procesar.')
        return 0

    mode_label = 'APPLY' if apply_mode else 'DRY-RUN'
    print(f'Modo: {mode_label} | Imágenes evaluadas: {len(targets)} | max_width={args.max_width} | quality={args.quality}')

    total_before = 0
    total_after = 0
    migrated_log: list[dict[str, Any]] = []

    for item in targets:
        url = item['original_url']
        is_webp = url.lower().endswith('.webp')
        raw = download_bytes(url)
        total_before += len(raw)

        if is_webp and not args.force:
            total_after += len(raw)
            print(f"  [SKIP] p={item['product_id']:2d} img={item['image_id']:2d} ya es WebP ({len(raw)/1024:.1f} KB)")
            continue

        webp_bytes, orig_dim, new_dim = convert_to_webp(raw, args.max_width, args.quality)
        total_after += len(webp_bytes)
        pct = (1 - len(webp_bytes) / max(len(raw), 1)) * 100
        stem = pathlib.Path(url.split('?')[0]).stem
        print(
            f"  [{mode_label}] p={item['product_id']:2d} img={item['image_id']:2d} "
            f"{orig_dim[0]}x{orig_dim[1]} -> {new_dim[0]}x{new_dim[1]} | "
            f"{len(raw)/1024:7.1f} KB -> {len(webp_bytes)/1024:6.1f} KB (-{pct:.1f}%)"
        )

        if apply_mode:
            new_url = upload_webp(img_server_url, img_api_key, webp_bytes, f'{stem}_800.webp')
            status_800 = verify_url_ok(new_url)
            status_400 = verify_url_ok(build_400_variant(new_url))
            if status_800 != 200 or status_400 != 200:
                raise RuntimeError(f'Verificación falló para {new_url}: 800={status_800}, 400={status_400}')
            update_db_image_url(
                item['image_id'], new_url, args.ssh_host, args.db_container, args.db_user, args.db_name
            )
            migrated_log.append({**item, 'new_url': new_url, 'before_bytes': len(raw), 'after_bytes': len(webp_bytes)})
            print(f'           OK 200 (800+400) -> {new_url}')

    total_pct = (1 - total_after / max(total_before, 1)) * 100
    print(f'Resumen {mode_label}: {total_before/1024:.1f} KB -> {total_after/1024:.1f} KB (-{total_pct:.1f}%)')

    if apply_mode and migrated_log:
        ts = dt.datetime.now().strftime('%Y-%m-%d_%H%M%S')
        log_path = args.backup_dir / f'migrated_{ts}.json'
        log_path.write_text(json.dumps(migrated_log, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f'Log de migración guardado en: {log_path}')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
