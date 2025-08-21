import React, { Fragment } from 'react';
import { Listbox, Transition } from '@headlessui/react';
import { CheckIcon, ChevronUpDownIcon } from '@heroicons/react/20/solid';

interface Option {
  value: string | number;
  label: string;
  disabled?: boolean;
}

interface SelectProps {
  name: string;
  label?: string;
  value?: string | number | (string | number)[];
  onChange: (value: string | number | (string | number)[]) => void;
  options: Option[];
  placeholder?: string;
  multiple?: boolean;
  disabled?: boolean;
  error?: string;
  required?: boolean;
  className?: string;
}

const Select: React.FC<SelectProps> = ({
  name,
  label,
  value,
  onChange,
  options,
  placeholder = 'Select an option',
  multiple = false,
  disabled = false,
  error,
  required = false,
  className = '',
}) => {
  const getDisplayValue = () => {
    if (!value) return placeholder;
    
    if (multiple && Array.isArray(value)) {
      if (value.length === 0) return placeholder;
      if (value.length === 1) {
        const option = options.find(opt => opt.value === value[0]);
        return option?.label || placeholder;
      }
      return `${value.length} items selected`;
    }
    
    const option = options.find(opt => opt.value === value);
    return option?.label || placeholder;
  };



  const handleChange = (newValue: string | number | (string | number)[]) => {
    onChange(newValue);
  };

  const selectId = `select-${name}`;

  return (
    <div className={`space-y-1 ${className}`}>
      {label && (
        <label htmlFor={selectId} className="block text-sm font-medium text-gray-700">
          {label}
          {required && <span className="text-danger-500 ml-1">*</span>}
        </label>
      )}
      
      <Listbox
        value={value}
        onChange={handleChange}
        multiple={multiple}
        disabled={disabled}
      >
        <div className="relative">
          <Listbox.Button
            id={selectId}
            className={`relative w-full cursor-default rounded-md border py-2 pl-3 pr-10 text-left shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-0 transition-colors duration-200 ${
              error
                ? 'border-danger-300 focus:ring-danger-500 focus:border-danger-500'
                : 'border-gray-300 focus:ring-primary-500 focus:border-primary-500'
            } ${
              disabled
                ? 'bg-gray-50 text-gray-500 cursor-not-allowed'
                : 'bg-white text-gray-900'
            } sm:text-sm`}
          >
            <span className="block truncate">{getDisplayValue()}</span>
            <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
              <ChevronUpDownIcon
                className="h-5 w-5 text-gray-400"
                aria-hidden="true"
              />
            </span>
          </Listbox.Button>

          <Transition
            as={Fragment}
            leave="transition ease-in duration-100"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <Listbox.Options className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
              {options.map((option) => (
                <Listbox.Option
                  key={option.value}
                  className={({ active }) =>
                    `relative cursor-default select-none py-2 pl-10 pr-4 ${
                      active ? 'bg-primary-100 text-primary-900' : 'text-gray-900'
                    } ${option.disabled ? 'opacity-50 cursor-not-allowed' : ''}`
                  }
                  value={option.value}
                  disabled={option.disabled}
                >
                  {({ selected }) => (
                    <>
                      <span
                        className={`block truncate ${
                          selected ? 'font-medium' : 'font-normal'
                        }`}
                      >
                        {option.label}
                      </span>
                      {selected ? (
                        <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-primary-600">
                          <CheckIcon className="h-5 w-5" aria-hidden="true" />
                        </span>
                      ) : null}
                    </>
                  )}
                </Listbox.Option>
              ))}
            </Listbox.Options>
          </Transition>
        </div>
      </Listbox>
      
      {error && (
        <p className="text-sm text-danger-600">{error}</p>
      )}
    </div>
  );
};

export default Select;
