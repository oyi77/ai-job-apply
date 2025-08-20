import React from 'react';
import { useFormContext, RegisterOptions } from 'react-hook-form';
import Input from '../ui/Input';

interface FormFieldProps {
  name: string;
  label?: string;
  type?: 'text' | 'email' | 'password' | 'textarea' | 'number';
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
  validation?: RegisterOptions;
}

const FormField: React.FC<FormFieldProps> = ({
  name,
  label,
  type = 'text',
  placeholder,
  required = false,
  disabled = false,
  className = '',
  validation = {},
}) => {
  const {
    register,
    formState: { errors },
    watch,
  } = useFormContext();

  const value = watch(name);
  const error = errors[name]?.message as string;

  return (
    <div className={className}>
      <Input
        {...register(name, { required: required ? `${label || name} is required` : false, ...validation })}
        name={name}
        label={label}
        type={type}
        placeholder={placeholder}
        value={value || ''}
        error={error}
        required={required}
        disabled={disabled}
        onChange={() => {}} // Handled by react-hook-form
      />
    </div>
  );
};

export default FormField;
