import React, { HTMLAttributes, useEffect, useRef, useState } from "react";
import { useSwipeable } from "react-swipeable";

interface TabProps extends HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const Tabs = ({ children, ...props }: TabProps) => {
  const [activeTab, setActiveTab] = useState(0);
  const [activeTabChanged, setActiveTabChanged] = useState(false);
  const [scrollOffset, setScrollOffset] = useState(0);

  const tabsContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setActiveTabChanged(true);
  }, [activeTab]);

  const childrenList = React.useMemo(() => {
    return React.Children.toArray(children);
  }, [children]);

  const handlers = useSwipeable({
    onSwipedLeft: () =>
      setActiveTab((prev) =>
        prev < childrenList.length - 1 ? prev + 1 : prev,
      ),
    onSwipedRight: () => setActiveTab((prev) => (prev > 0 ? prev - 1 : prev)),
  });

  useEffect(() => {
    if (!activeTabChanged) {
      return;
    }

    if (
      !tabsContainerRef.current ||
      tabsContainerRef.current.children.length === 0
    ) {
      return;
    }
    setActiveTabChanged(false);
    const activeTabElement = tabsContainerRef.current.children[
      activeTab
    ] as HTMLElement;
    console.log(
      "Active Tab Element",
      activeTabElement.offsetLeft,
      activeTabElement.offsetWidth,
    );
    console.log(
      "Tabs Container",
      tabsContainerRef.current.offsetWidth,
      tabsContainerRef.current.offsetLeft,
    );
    console.log("Scroll Offset", scrollOffset);

    setScrollOffset(
      activeTabElement.offsetLeft +
        activeTabElement.offsetWidth / 2 -
        tabsContainerRef.current.offsetWidth / 2,
    );
  }, [activeTab, tabsContainerRef, activeTabChanged, scrollOffset]);
  const activateTab = React.useCallback(
    (event: React.MouseEvent<HTMLDivElement>, index: number) => {
      setActiveTab(index);
      event.preventDefault();
      event.stopPropagation();
    },
    [],
  );

  console.log(scrollOffset);
  return (
    <div
      {...handlers}
      ref={tabsContainerRef}
      className="flex flex-row overflow-hidden max-w-full cursor-pointer whitespace-nowrap scroll-smooth transition-all delay-150"
      style={
        childrenList.length > 0
          ? {
              transform: `translateX(${-scrollOffset}px)`,
            }
          : {}
      }
      {...props}
    >
      {childrenList.map((tab, index) => (
        <div
          key={index}
          className={`transition-all ease-in-out duration-300 ${
            index === activeTab
              ? "w-full z-10 opacity-100"
              : "w-4/5 z-0 opacity-50"
          }`}
          onClick={(event) => activateTab(event, index)}
          style={{
            transform: index === activeTab ? "scale(1.0)" : "scale(0.8)",
          }}
        >
          {tab}
        </div>
      ))}
    </div>
  );
};
