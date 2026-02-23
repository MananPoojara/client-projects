export class PhoneNumber {
  private readonly value: string;

  constructor(phone: string) {
    const normalized = this.normalize(phone);
    if (!this.isValid(normalized)) {
      throw new Error('Invalid phone number format');
    }
    this.value = normalized;
  }

  private normalize(phone: string): string {
    return phone.replace(/[\s\-\(\)]/g, '').trim();
  }

  private isValid(phone: string): boolean {
    const phoneRegex = /^\+?[\d\s\-()]+$/;
    return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 10;
  }

  getValue(): string {
    return this.value;
  }

  equals(other: PhoneNumber): boolean {
    return this.value === other.value;
  }
}
