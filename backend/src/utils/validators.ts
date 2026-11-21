/**
 * Validation utilities for forms and user inputs
 */

export function isValidEmail(email: string): boolean {
  if (!email) return false;
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email.trim());
}

export function isValidUrl(url: string): boolean {
  if (!url) return false;
  try {
    const parsed = new URL(url.startsWith('http') ? url : `https://${url}`);
    return parsed.protocol === 'http:' || parsed.protocol === 'https:';
  } catch {
    return false;
  }
}

export function isValidPhone(phone: string): boolean {
  if (!phone) return false;
  // Allows optional +, numbers, dashes, parentheses and spaces, length 7-20
  const phoneRegex = /^(\+?\d{1,4}[ -]?)?(\(?\d{2,5}\)?[ -]?)?\d{3,5}[ -]?\d{3,5}$/;
  return phoneRegex.test(phone.trim());
}

export interface PasswordStrength {
  score: number; // 0 to 4
  label: 'Very Weak' | 'Weak' | 'Fair' | 'Strong' | 'Very Strong';
  color: string;
  feedback: string[];
}

export function checkPasswordStrength(password: string): PasswordStrength {
  if (!password) {
    return {
      score: 0,
      label: 'Very Weak',
      color: 'text-rose-500',
      feedback: ['Password is required'],
    };
  }

  let score = 0;
  const feedback: string[] = [];

  if (password.length >= 8) {
    score += 1;
  } else {
    feedback.push('Use at least 8 characters');
  }

  if (/[A-Z]/.test(password) && /[a-z]/.test(password)) {
    score += 1;
  } else {
    feedback.push('Use both uppercase and lowercase letters');
  }

  if (/\d/.test(password)) {
    score += 1;
  } else {
    feedback.push('Add at least one number');
  }

  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    score += 1;
  } else {
    feedback.push('Add at least one special character');
  }

  const levels: Array<{ label: PasswordStrength['label']; color: string }> = [
    { label: 'Very Weak', color: 'text-rose-500' },
    { label: 'Weak', color: 'text-amber-500' },
    { label: 'Fair', color: 'text-yellow-500' },
    { label: 'Strong', color: 'text-blue-500' },
    { label: 'Very Strong', color: 'text-emerald-500' },
  ];

  return {
    score,
    label: levels[score].label,
    color: levels[score].color,
    feedback,
  };
}
