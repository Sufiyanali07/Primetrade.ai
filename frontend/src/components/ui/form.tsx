import * as React from "react";
import { Controller, useFormContext } from "react-hook-form";
import type { ControllerProps, FieldPath, FieldValues } from "react-hook-form";
import { cn } from "@/lib/utils";
import { Label } from "@/components/ui/label";

export interface FormFieldContextValue {
  name: string;
}

const FormFieldContext = React.createContext<FormFieldContextValue | null>(null);

const useFormField = () => {
  const ctx = React.useContext(FormFieldContext);
  if (!ctx) throw new Error("useFormField must be used within FormField");
  const form = useFormContext();
  const state = form.formState;
  return {
    ...ctx,
    form,
    invalid: !!state.errors[ctx.name],
    error: state.errors[ctx.name]?.message as string | undefined,
  };
};

function FormField<
  TFieldValues extends FieldValues,
  TName extends FieldPath<TFieldValues>,
>(props: ControllerProps<TFieldValues, TName>) {
  const { name } = props;
  return (
    <FormFieldContext.Provider value={{ name: name as string }}>
      <Controller {...props} />
    </FormFieldContext.Provider>
  );
}

const FormItem = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("space-y-2", className)} {...props} />
  )
);
FormItem.displayName = "FormItem";

const FormLabel = React.forwardRef<
  React.ElementRef<typeof Label>,
  React.ComponentPropsWithoutRef<typeof Label>
>(({ className, ...props }, ref) => {
  const { error } = useFormField();
  return (
    <Label ref={ref} className={cn(error && "text-destructive", className)} {...props} />
  );
});
FormLabel.displayName = "FormLabel";

const FormControl = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ ...props }, ref) => <div ref={ref} {...props} />
);
FormControl.displayName = "FormControl";

const FormMessage = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLParagraphElement>>(
  ({ className, children, ...props }, ref) => {
    const { error } = useFormField();
    return (
      <p
        ref={ref}
        className={cn("text-sm font-medium text-destructive", className)}
        {...props}
      >
        {error ?? children}
      </p>
    );
  }
);
FormMessage.displayName = "FormMessage";

export { FormField, FormItem, FormLabel, FormControl, FormMessage, useFormField };
