import api from '../config/api';

export interface WelcomeEmailRequest {
  to: string;
  display_name?: string;
}

export interface NotificationEmailRequest {
  to: string;
  title: string;
  message: string;
  action_url?: string;
}

export interface OrderConfirmationEmailRequest {
  to: string;
  order_number: string;
  order_date: string;
  customer_name: string;
  order_items: any[];
  subtotal: number;
  discount?: number;
  shipping_cost: number;
  total: number;
  shipping_address: string;
  shipping_city: string;
  shipping_postal_code: string;
  delivery_notes?: string;
  payment_method_text: string;
  payment_instructions?: string;
}

export interface ContactEmailRequest {
  customer_name: string;
  customer_email: string;
  customer_phone?: string;
  subject: string;
  message: string;
  priority?: 'low' | 'medium' | 'high';
}

export interface EmailResponse {
  message: string;
  [key: string]: any;
}

class EmailService {
  /**
   * Send welcome email to new user
   */
  async sendWelcomeEmail(request: WelcomeEmailRequest): Promise<EmailResponse> {
    try {
      const response = await api.post('/emails/welcome', request);
      return response.data;
    } catch (error) {
      throw new Error('Error al enviar email de bienvenida');
    }
  }

  /**
   * Send notification email
   */
  async sendNotificationEmail(request: NotificationEmailRequest): Promise<EmailResponse> {
    try {
      const response = await api.post('/emails/notify', request);
      return response.data;
    } catch (error) {
      throw new Error('Error al enviar email de notificación');
    }
  }

  /**
   * Send order confirmation email
   */
  async sendOrderConfirmationEmail(request: OrderConfirmationEmailRequest): Promise<EmailResponse> {
    try {
      const response = await api.post('/emails/order-confirmation', request);
      return response.data;
    } catch (error) {
      throw new Error('Error al enviar email de confirmación de pedido');
    }
  }

  /**
   * Send contact form email
   */
  async sendContactEmail(request: ContactEmailRequest): Promise<EmailResponse> {
    try {
      const response = await api.post('/emails/contact', request);
      return response.data;
    } catch (error) {
      throw new Error('Error al enviar mensaje de contacto');
    }
  }
}

// Email Verification Service
export interface VerifyEmailRequest {
  token?: string;
  code?: string;
  email: string;
}

export interface VerifyEmailResponse {
  success: boolean;
  message: string;
  verified?: boolean;
}

export interface ResendVerificationRequest {
  email: string;
}

class EmailVerificationService {
  /**
   * Verify email using token or code
   */
  async verifyEmail(request: VerifyEmailRequest): Promise<VerifyEmailResponse> {
    try {
      const response = await api.post('/email-verification/verify', request);
      return response.data;
    } catch (error) {
      throw new Error('Error al verificar email');
    }
  }

  /**
   * Resend verification email
   */
  async resendVerificationEmail(request: ResendVerificationRequest): Promise<EmailResponse> {
    try {
      const response = await api.post('/email-verification/resend-verification', request);
      return response.data;
    } catch (error) {
      throw new Error('Error al reenviar email de verificación');
    }
  }

  /**
   * Get verification status for a user
   */
  async getVerificationStatus(userId: number): Promise<any> {
    try {
      const response = await api.get(`/email-verification/status/${userId}`);
      return response.data;
    } catch (error) {
      throw new Error('Error obteniendo estado de verificación');
    }
  }
}

// Export singleton instances
export const emailService = new EmailService();
export const emailVerificationService = new EmailVerificationService();
export default emailService;
