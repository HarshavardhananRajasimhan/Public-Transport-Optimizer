import React from 'react';

export const IllustrativeErrorIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
    <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" {...props}>
        <defs>
            <linearGradient id="gradError" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style={{stopColor: 'rgb(239, 68, 68)', stopOpacity:1}} />
                <stop offset="100%" style={{stopColor: 'rgb(249, 115, 22)', stopOpacity:1}} />
            </linearGradient>
            <linearGradient id="gradErrorBg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style={{stopColor: 'rgb(254, 226, 226)', stopOpacity:1}} />
                <stop offset="100%" style={{stopColor: 'rgb(255, 237, 213)', stopOpacity:1}} />
            </linearGradient>
        </defs>
        <circle cx="100" cy="100" r="80" fill="url(#gradErrorBg)" />
        <circle cx="100" cy="100" r="60" fill="url(#gradError)" stroke="#fff" strokeWidth="8"/>
        <g transform="translate(65, 65) scale(3.5)" fill="#fff">
            <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
        </g>
    </svg>
);