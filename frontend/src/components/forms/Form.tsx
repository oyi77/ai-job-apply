import React from 'react';
import { useForm, FormProvider, FieldValues, UseFormProps } from 'react-hook-form';

interface FormProps<T extends FieldValues> extends UseFormProps<T> {
  children: React.ReactNode;
  onSubmit: (data: T) => void | Promise<void>;
  className?: string;
}

function Form<T extends FieldValues>({
  children,
  onSubmit,
  className = '',
  ...formProps
}: FormProps<T>) {
  const methods = useForm<T>(formProps);
  
  const handleSubmit = async (data: T) => {
    try {
      await onSubmit(data);
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };

  return (
    <FormProvider {...methods}>
      <form 
        onSubmit={methods.handleSubmit(handleSubmit)} 
        className={`space-y-6 ${className}`}
        noValidate
      >
        {children}
      </form>
    </FormProvider>
  );
}

export default Form;
