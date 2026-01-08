'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { auth } from '@/lib/auth';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to tasks if already authenticated
    if (auth.isAuthenticated()) {
      router.push('/tasks');
    }
  }, [router]);

  return (
    <div className="flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-accent-50 relative overflow-hidden py-20">
      {/* Animated gradient blobs */}
      <div className="absolute -top-40 -right-40 w-96 h-96 bg-gradient-to-br from-primary-400/20 to-accent-400/20 rounded-full blur-3xl animate-pulse-soft" />
      <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-gradient-to-br from-accent-400/20 to-primary-400/20 rounded-full blur-3xl animate-pulse-soft" style={{ animationDelay: '1s' }} />

      <div className="relative z-10 max-w-5xl mx-auto px-6 py-12 text-center animate-fadeIn">
        {/* Hero Section */}
        <div className="animate-slideUp">
          <h1 className="text-5xl md:text-6xl font-bold text-neutral-900 leading-tight tracking-tighter">
            Organize Your Life,<br />
            <span className="text-primary-600">One Task at a Time</span>
          </h1>

          <p className="mt-6 text-lg md:text-xl text-neutral-600 max-w-2xl mx-auto leading-relaxed">
            A beautifully simple todo app that helps you focus on what matters.
            Stay organized, boost productivity, and achieve your goals.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/signup"
              className="px-8 py-4 bg-primary-600 hover:bg-primary-700 active:bg-primary-800 text-white text-lg font-semibold tracking-wide rounded-xl shadow-lg hover:shadow-2xl transform hover:scale-105 active:scale-95 transition-all duration-300 ease-out focus:outline-none focus:ring-4 focus:ring-primary-200"
            >
              Get Started Free
            </Link>

            <Link
              href="/signin"
              className="px-8 py-4 bg-white hover:bg-neutral-50 text-primary-600 text-lg font-semibold tracking-wide border-2 border-neutral-300 hover:border-primary-600 rounded-xl shadow-md hover:shadow-lg transform hover:scale-105 active:scale-95 transition-all duration-300 ease-out focus:outline-none focus:ring-4 focus:ring-primary-200"
            >
              Sign In
            </Link>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              icon: '✓',
              title: 'Simple & Intuitive',
              description: 'Clean interface designed for effortless task management',
            },
            {
              icon: '⚡',
              title: 'Lightning Fast',
              description: 'Optimized performance for instant updates and responses',
            },
            {
              icon: '🔒',
              title: 'Secure & Private',
              description: 'Your data is encrypted and protected at all times',
            },
          ].map((feature, index) => (
            <div
              key={feature.title}
              className="group bg-white rounded-2xl p-8 border border-neutral-200 hover:border-primary-300 shadow-md hover:shadow-xl transform hover:-translate-y-2 transition-all duration-300 ease-out animate-slideUp"
              style={{ animationDelay: `${index * 100}ms`, animationFillMode: 'backwards' }}
            >
              <div className="w-14 h-14 bg-primary-100 group-hover:bg-primary-600 text-primary-600 group-hover:text-white text-3xl rounded-xl flex items-center justify-center transform group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 mx-auto">
                {feature.icon}
              </div>

              <h3 className="mt-6 text-xl font-semibold text-neutral-900">
                {feature.title}
              </h3>

              <p className="mt-3 text-neutral-600 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
