import React, {
  HTMLAttributes,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { useSwipeable } from "react-swipeable";

interface TabProps extends HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const Tabs = ({ children, ...props }: TabProps) => {
  const [activeTab, setActiveTab] = useState(0);
  const [activeTabChanged, setActiveTabChanged] = useState(false);
  const [scrollOffset, setScrollOffset] = useState(0);

  const tabsContainerRef = useRef<HTMLDivElement>(null);
  const [isDesktop, setIsDesktop] = useState(false);
  // rest of your component setup

  // This effect sets up a listener for window resize events
  // and updates `isDesktop` based on the window width.
  useEffect(() => {
    const checkIfDesktop = () => {
      setIsDesktop(window.innerWidth > 768); // Tailwind's 'md' breakpoint
    };

    // Check on mount and add event listener for future resizes
    checkIfDesktop();
    window.addEventListener("resize", checkIfDesktop);

    // Cleanup listener on component unmount
    return () => window.removeEventListener("resize", checkIfDesktop);
  }, []);

  useEffect(() => {
    setActiveTabChanged(true);
  }, [activeTab]);

  const childrenList = React.useMemo(() => {
    return React.Children.toArray(children);
  }, [children]);

  const handlers = useSwipeable({
    onSwipedLeft: () => {
      console.log("swiped left");
      setActiveTab((prev) =>
        prev < childrenList.length - 1 ? prev + 1 : prev,
      );
    },
    onSwipedRight: () => {
      console.log("swiped right");
      setActiveTab((prev) => (prev > 0 ? prev - 1 : prev));
    },
    preventScrollOnSwipe: true,
  });

  useEffect(() => {
    if (!tabsContainerRef.current) {
      return;
    }
    const currentRef = tabsContainerRef.current;

    tabsContainerRef.current.onscroll = () => {
      console.log("Scrolled");
    };

    tabsContainerRef.current.addEventListener("scroll", () => {
      console.log("Scrolled");
    });

    return () => {
      currentRef.removeEventListener("scroll", () => {
        console.log("Scrolled");
      });
    };
  }, []);

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
      activeTabElement.scrollLeft,
      activeTabElement.scrollWidth,
    );
    console.log(
      "Tabs Container",
      tabsContainerRef.current.offsetWidth,
      tabsContainerRef.current.offsetLeft,
      tabsContainerRef.current.scrollLeft,
      tabsContainerRef.current.scrollWidth,
      window.scrollX,
      window.innerWidth,
    );
    console.log("Scroll Offset", scrollOffset);

    const newScrollOffset = isDesktop
      ? activeTabElement.offsetLeft +
        activeTabElement.offsetWidth / 2 -
        tabsContainerRef.current.offsetWidth / 2
      : activeTabElement.offsetLeft;
    setScrollOffset(newScrollOffset);
  }, [activeTab, tabsContainerRef, activeTabChanged, scrollOffset, isDesktop]);
  const activateTab = React.useCallback(
    (event: React.MouseEvent<HTMLDivElement>, index: number) => {
      setActiveTab(index);
    },
    [],
  );

  console.log(scrollOffset);
  return (
    <div
      {...handlers}
      className="h-full relative overflow-y-hidden overflow-x-hidden"
    >
      <div
        ref={tabsContainerRef}
        className="flex h-full flex-row overflow-x-visible
          md:w-full w-fit cursor-pointer whitespace-nowrap
          transition-all delay-150"
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
            className={`transition-all ease-in-out duration-300 w-screen  ${
              index === activeTab
                ? "z-10 opacity-100 cursor-default"
                : "z-0 opacity-50"
            }`}
            onClick={(event) => activateTab(event, index)}
            style={{
              transform: index === activeTab ? "scale(1.0)" : "scale(0.8)",
            }}
          >
            <div
              className={`w-full h-full ${
                index === activeTab ? "" : "pointer-events-none"
              }`}
            >
              {tab}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
