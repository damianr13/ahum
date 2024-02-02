import React from "react";
// Icons from Heroicons: https://heroicons.com/ for demonstration
// Ensure you have these icons or similar ones from another library
import { FaDiscord, FaGithub, FaMediumM } from "react-icons/fa";

const TopBar = () => {
  return (
    <div className="bg-gray-800 text-white py-4 px-8 flex justify-between items-center">
      <img src="/logo.png" className="h-20" alt="logo" />
      <h1 className="text-2xl font-bold">Ahum</h1>
      <div className="flex items-center gap-4">
        {/* Discord Button */}
        <a
          href="https://discord.com"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:bg-gray-700 p-2 rounded transition-colors duration-300"
        >
          <FaDiscord className="h-6 w-6" />
        </a>
        {/* GitHub Button */}
        <a
          href="https://github.com"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:bg-gray-700 p-2 rounded transition-colors duration-300"
        >
          <FaGithub className="h-6 w-6" />
        </a>
        {/* Medium Button */}
        <a
          href="https://medium.com"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:bg-gray-700 p-2 rounded transition-colors duration-300"
        >
          <FaMediumM className="h-6 w-6" />
        </a>
      </div>
    </div>
  );
};

export default TopBar;
