import React from 'react';

interface MapMetroIconProps extends React.SVGProps<SVGSVGElement> {
  isLive?: boolean;
}

export const MapMetroIcon: React.FC<MapMetroIconProps> = ({ isLive = false, ...props }) => {
  const containerClasses = "relative";
  const svgClasses = isLive
    ? "w-7 h-7 text-purple-500 drop-shadow-md animate-pulse-live"
    : "w-8 h-8 text-purple-600 drop-shadow-lg";
  
  return (
    <div className={containerClasses}>
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className={svgClasses} {...props}>
        <path d="M12 5.25a.75.75 0 0 0-1.06.02L6.75 9.456a.75.75 0 0 0-.02 1.06c.277.313.73.355 1.033.093l.298-.261A9.752 9.752 0 0 1 12 9a9.752 9.752 0 0 1 3.939 1.348l.298.26c.303.262.756.22 1.033-.092a.75.75 0 0 0-.02-1.06L13.06 5.27a.75.75 0 0 0-1.06-.02Z" />
        <path fillRule="evenodd" d="M12 21a8.25 8.25 0 0 0 6.638-3.443.75.75 0 0 0-.453-1.218H5.815a.75.75 0 0 0-.453 1.218A8.25 8.25 0 0 0 12 21ZM12 10.5a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-1.5 0v-1.5a.75.75 0 0 1 .75-.75Zm-3 3a.75.75 0 0 0 0 1.5h6a.75.75 0 0 0 0-1.5h-6Z" clipRule="evenodd" />
      </svg>
    </div>
  );
};
