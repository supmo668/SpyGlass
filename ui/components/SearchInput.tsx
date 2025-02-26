import React, { useState } from "react";
import { SendHorizontal } from "lucide-react";
import { cn } from "@/lib/utils";

interface SearchInputProps {
  onSearch?: (query: string) => void;
  className?: string;
  placeholder?: string;
  value?: string;
}

const SearchInput = ({
  onSearch,
  className,
  placeholder = "Search trends...",
  value: initialValue = "",
}: SearchInputProps) => {
  const [query, setQuery] = useState(initialValue);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSearch && query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <div className="w-full flex justify-center">
      <form
        onSubmit={handleSubmit}
        className={cn(
          "w-full max-w-3xl bg-gray-100 bg-opacity-20 backdrop-blur-lg",
          "rounded-3xl shadow-md",
          "hover:bg-opacity-30 transition-all duration-200",
          className
        )}
      >
        <div className="relative flex items-center gap-2 p-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={placeholder}
            className={cn(
              "flex-1 bg-transparent border-none outline-none",
              "py-6 px-6 text-base placeholder:text-gray-500",
              "focus:ring-2 focus:ring-gray-500 focus:border-gray-500 rounded-3xl",
              "transition-all duration-200"
            )}
          />
          <button
            type="submit"
            className={cn(
              "p-3 rounded-2xl bg-gray-700 hover:bg-gray-800",
              "text-white shadow-sm hover:shadow-md",
              "transition-all duration-200"
            )}
          >
            <SendHorizontal className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
};

export default SearchInput;