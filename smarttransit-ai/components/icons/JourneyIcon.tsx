import React from 'react';

export const JourneyIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
    <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" {...props}>
      <defs>
        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{stopColor: 'rgb(79, 70, 229)', stopOpacity:1}} />
          <stop offset="100%" style={{stopColor: 'rgb(59, 130, 246)', stopOpacity:1}} />
        </linearGradient>
        <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{stopColor: 'rgb(129, 140, 248)', stopOpacity:1}} />
          <stop offset="100%" style={{stopColor: 'rgb(96, 165, 250)', stopOpacity:1}} />
        </linearGradient>
      </defs>
      <path fill="url(#grad2)" d="M50,150 C20,150 20,100 50,100 C80,100 80,50 110,50 C140,50 140,100 170,100 C200,100 200,150 170,150 Z" opacity="0.1"></path>
      
      <circle cx="50" cy="110" r="12" fill="url(#grad1)" stroke="#fff" strokeWidth="4"/>
      <circle cx="150" cy="70" r="12" fill="url(#grad1)" stroke="#fff" strokeWidth="4"/>

      <path d="M 58 102 C 80 85, 120 85, 142 78" stroke="url(#grad1)" strokeWidth="6" fill="none" strokeLinecap="round" strokeDasharray="10 10">
        <animate attributeName="stroke-dashoffset" from="0" to="20" dur="1s" repeatCount="indefinite" />
      </path>

      <g transform="translate(35, 95) scale(0.18)">
        <path fill="#fff" d="M12,2A10,10,0,0,0,2,12A10,10,0,0,0,12,22A10,10,0,0,0,22,12A10,10,0,0,0,12,2M12,4A8,8,0,0,1,20,12H17A5,5,0,0,0,12,7V4M12,20A8,8,0,0,1,4,12H7A5,5,0,0,0,12,17V20Z"/>
      </g>
      <g transform="translate(135, 55) scale(0.18)">
        <path fill="#fff" d="M12,2A10,10,0,0,0,2,12A10,10,0,0,0,12,22A10,10,0,0,0,22,12A10,10,0,0,0,12,2M12,7A5,5,0,0,0,7,12H4A8,8,0,0,1,12,4V7M17,12A5,5,0,0,0,12,7V4A8,8,0,0,1,20,12H17Z"/>
      </g>
    </svg>
);