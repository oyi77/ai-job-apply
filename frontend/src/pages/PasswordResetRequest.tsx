import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Card, CardHeader, CardBody, CardFooter } from '@/components/ui/Card';
import Alert from '@/components/ui/Alert';
import Spinner from '@/components/ui/Spinner';

export const PasswordResetRequest = () => {
    const [email, setEmail] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            const response = await fetch('/api/v1/auth/request-password-reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email }),
            });

            if (!response.ok) {
                throw new Error('Failed to request password reset');
            }

            setIsSubmitted(true);
        } catch (err) {
            setError('An error occurred. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    if (isSubmitted) {
        return (
            <div className="container flex h-screen w-screen flex-col items-center justify-center">
                <Card className="w-[350px]">
                    <CardHeader
                        title="Check your email"
                        description={`We have sent a password reset link to ${email}`}
                    />
                    <CardBody>
                        <p className="text-sm text-muted-foreground">
                            Click the link in the email to reset your password. If you don't see the email, check your spam folder.
                        </p>
                    </CardBody>
                    <CardFooter>
                        <Link to="/login" className="w-full">
                            <Button variant="secondary" className="w-full">
                                Back to Login
                            </Button>
                        </Link>
                    </CardFooter>
                </Card>
            </div>
        );
    }

    return (
        <div className="container flex h-screen w-screen flex-col items-center justify-center">
            <Card className="w-[350px]">
                <CardHeader
                    title="Reset Password"
                    description="Enter your email address and we'll send you a link to reset your password"
                />
                <CardBody>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {error && (
                            <Alert type="error" message={error} />
                        )}
                        <div className="space-y-2">
                            <Input
                                id="email"
                                name="email"
                                type="email"
                                label="Email"
                                placeholder="name@example.com"
                                value={email}
                                onChange={(val: string | React.ChangeEvent<HTMLInputElement>) => {
                                    // Handle both string (from Input component) and event object
                                    const value = typeof val === 'string' ? val : val.target.value;
                                    setEmail(value);
                                }}
                                required
                            />
                        </div>
                        <Button className="w-full" type="submit" disabled={isLoading}>
                            {isLoading && (
                                <span className="mr-2"><Spinner size="sm" /></span>
                            )}
                            Send Reset Link
                        </Button>
                    </form>
                </CardBody>
                <CardFooter className="flex flex-col space-y-2">
                    <Link to="/login" className="text-sm text-primary hover:underline">
                        Back to Login
                    </Link>
                </CardFooter>
            </Card>
        </div>
    );
};
