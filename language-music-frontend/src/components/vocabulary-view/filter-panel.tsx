import React, { Fragment, useEffect, useMemo, useState } from "react";
import { Menu, Transition } from "@headlessui/react";
import {
  CEFR_LEVEL_KEY,
  PART_OF_SPEECH_KEY,
  VocabularyFilter,
} from "@/components/vocabulary-view/types";

interface FilterPanelProps {
  onFilterChange: (filter: VocabularyFilter) => void;
}

const FilterPanel = (props: FilterPanelProps) => {
  const [selectedOptions, setSelectedOptions] = useState<VocabularyFilter>({
    [CEFR_LEVEL_KEY]: new Set<string>(),
    [PART_OF_SPEECH_KEY]: new Set<string>(),
  });

  const humanReadableCategoryName = useMemo<{ [key: string]: string }>(() => {
    return {
      [CEFR_LEVEL_KEY]: "CEFR Level",
      [PART_OF_SPEECH_KEY]: "Part of Speech",
    };
  }, []);

  useEffect(() => {
    props.onFilterChange(selectedOptions);
  }, [props, selectedOptions]);

  const handleSelect = (
    category: string,
    value: string,
    event: React.MouseEvent<HTMLElement>,
  ) => {
    // Clone the current state to avoid direct mutation
    const newSelectedOptions = { ...selectedOptions };
    // Toggle the option in the set
    if (newSelectedOptions[category].has(value)) {
      newSelectedOptions[category].delete(value);
    } else {
      newSelectedOptions[category].add(value);
    }
    // Update the state with the new set
    setSelectedOptions(newSelectedOptions);

    // We don't want to close the menu after selecting an option
    event.preventDefault();
    event.stopPropagation();
  };

  const categories = {
    [CEFR_LEVEL_KEY]: ["A1", "A2", "B1", "B2", "C1", "C2", "??"],
    [PART_OF_SPEECH_KEY]: [
      "substantive",
      "adjective",
      "verb",
      "adverb",
      "conjuction",
      "interjection",
    ],
  };

  return (
    <Menu as="div" className="relative inline-block text-left">
      <div className=" hover:shadow-2xl hover:translate-x-0.5 hover:translate-y-0.5">
        <Menu.Button className="inline-flex w-full justify-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 -960 960 960"
            className="w-6 h-6 fill-white"
          >
            <path d="M400-240v-80h160v80H400ZM240-440v-80h480v80H240ZM120-640v-80h720v80H120Z" />
          </svg>
        </Menu.Button>
      </div>

      <Transition
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Items
          static
          className="absolute right-0 z-10 w-72 mt-2 origin-top-right bg-gray-700 divide-y divide-gray-100
          rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
        >
          {Object.entries(categories).map(([category, options]) => (
            <div className="py-1" key={category}>
              <div className="px-4 py-2 text-xs text-gray-400">
                {humanReadableCategoryName[category]}
              </div>
              <div className="grid grid-cols-2 gap-1 px-2">
                {options.map((option) => (
                  <Menu.Item key={option}>
                    {({ active }) => (
                      <button
                        className={`${
                          active ? "bg-gray-100 text-gray-900" : "text-white"
                        } ${
                          selectedOptions[category].has(option)
                            ? "bg-blue-500 text-white"
                            : ""
                        } group flex w-full items-center justify-center px-2 py-2 text-sm rounded-md`}
                        onClick={(e) => handleSelect(category, option, e)}
                      >
                        {option}
                      </button>
                    )}
                  </Menu.Item>
                ))}
              </div>
            </div>
          ))}
        </Menu.Items>
      </Transition>
    </Menu>
  );
};

export default FilterPanel;
