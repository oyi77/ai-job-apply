import React, { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Card, CardHeader, CardBody, CardFooter } from '@/components/ui/Card';
import Alert from '@/components/ui/Alert';
import Spinner from '@/components/ui/Spinner';
import { CheckCircleIcon } from '@heroicons/react/24/solid';

export const PasswordReset = () => {
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token');
    const navigate = useNavigate();

    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [isSuccess, setIsSuccess] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (password.length < 8) {
            setError('Password must be at least 8 characters long');
            return;
        }

        setIsLoading(true);

        try {
            const response = await fetch('/api/v1/auth/reset-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token, new_password: password }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to reset password');
            }

            setIsSuccess(true);
            setTimeout(() => navigate('/login'), 3000);
        } catch (err: any) {
            setError(err.message || 'An error occurred. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    if (!token) {
        return (
            <div className="container flex h-screen w-screen flex-col items-center justify-center">
                <Card className="w-[350px]">
                    <CardHeader
                        title="Invalid Link"
                        description="This password reset link is invalid or has expired."
                    />
                    <CardFooter>
                        <Link to="/login/reset" className="w-full">
                            <Button className="w-full">
                                Request New Link
                            </Button>
                        </Link>
                    </CardFooter>
                </Card>
            </div>
        );
    }

    if (isSuccess) {
        return (
            <div className="container flex h-screen w-screen flex-col items-center justify-center">
                <Card className="w-[350px]">
                    <CardHeader
                        title="Password Reset Successful"
                        description="Your password has been reset. Redirecting to login..."
                    />
                    <CardBody>
                        <CheckCircleIcon className="mx-auto h-12 w-12 text-green-500" />
                    </CardBody>
                    <CardFooter>
                        <Link to="/login" className="w-full">
                            <Button className="w-full">
                                Login Now
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
                    title="Set New Password"
                    description="Enter your new password below."
                />
                <CardBody>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {error && (
                            <Alert type="error" message={error} />
                        )}
                        <div className="space-y-2">
                            <Input
                                id="password"
                                name="new-password"
                                type="password"
                                label="New Password"
                                value={password}
                                onChange={(val: string | React.ChangeEvent<HTMLInputElement>) => {
                                    const value = typeof val === 'string' ? val : val.target.value;
                                    setPassword(value);
                                }}
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <Input
                                id="confirmPassword"
                                name="confirm-password"
                                type="password"
                                label="Confirm Password"
                                value={confirmPassword}
                                onChange={(val: string | React.ChangeEvent<HTMLInputElement>) => {
                                    const value = typeof val === 'string' ? val : val.target.value;
                                    setConfirmPassword(value);
                                }}
                                required
                            />
                        </div>
                        <Button className="w-full" type="submit" disabled={isLoading}>
                            {isLoading && (
                                <span className="mr-2"><Spinner size="sm" /></span>
                            )}
                            Reset Password
                        </Button>
                    </form>
                </CardBody>
            </Card>
        </div>
    );
};
