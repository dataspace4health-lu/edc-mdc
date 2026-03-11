import React, { memo, useState, useRef, useEffect, useCallback } from "react";
import { createPortal } from "react-dom";

export type TooltipPosition = "top" | "bottom" | "left" | "right";

export type TooltipProps = {
  children: React.ReactNode;
  text: string;
  preferredPosition?: TooltipPosition;
  className?: string;
  offset?: number;
};

type CalculatedPosition = {
  position: TooltipPosition;
  adjustedOffset: { x: number; y: number };
  x?: number;
  y?: number;
};

const getPositionClasses = (position: TooltipPosition): string => {
  const baseClasses =
    "fixed whitespace-nowrap rounded bg-black px-2 py-1 text-white opacity-0 transition-opacity duration-200 z-[9999] pointer-events-none text-sm";

  const arrowClasses = {
    top: "after:top-full after:left-1/2 after:-translate-x-1/2 after:border-t-black after:border-l-transparent after:border-r-transparent after:border-b-transparent",
    bottom:
      "after:bottom-full after:left-1/2 after:-translate-x-1/2 after:border-b-black after:border-l-transparent after:border-r-transparent after:border-t-transparent",
    left: "after:left-full after:top-1/2 after:-translate-y-1/2 after:border-l-black after:border-t-transparent after:border-b-transparent after:border-r-transparent",
    right:
      "after:right-full after:top-1/2 after:-translate-y-1/2 after:border-r-black after:border-t-transparent after:border-b-transparent after:border-l-transparent",
  };

  return `${baseClasses} after:absolute after:border-4 ${arrowClasses[position]}`;
};

const Tooltip: React.FC<TooltipProps> = memo(
  ({ children, text, preferredPosition = "top", className = "", offset = 8 }) => {
    const hasTooltipText = !!text?.trim();

    const [isVisible, setIsVisible] = useState(false);
    const [calculatedPosition, setCalculatedPosition] = useState<CalculatedPosition>({
      position: preferredPosition,
      adjustedOffset: { x: 0, y: 0 },
    });

    const triggerRef = useRef<HTMLSpanElement>(null);

    const calculateBestPosition = useCallback((): CalculatedPosition => {
      if (!triggerRef.current) {
        return { position: preferredPosition, adjustedOffset: { x: 0, y: 0 } };
      }

      const triggerRect = triggerRef.current.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      // Calculate precise tooltip dimensions using canvas
      let tooltipWidth = 120; // fallback
      let tooltipHeight = 32;

      const canvas = document.createElement("canvas");
      const context = canvas.getContext("2d");
      if (context) {
        context.font = "14px system-ui, -apple-system, sans-serif"; // text-sm equivalent
        const textWidth = context.measureText(text).width;
        // Add padding: px-2 py-1 = 8px horizontal padding total
        tooltipWidth = Math.ceil(textWidth) + 16; // 8px left + 8px right padding
        tooltipHeight = 32; // approximate height with padding
      } else {
        // Fallback if canvas not available
        tooltipWidth = Math.max(text.length * 8 + 16, 60); // rough estimate
      }

      canvas.remove();

      let x = 0,
        y = 0;

      switch (preferredPosition) {
        case "top":
          // Center the tooltip exactly over the trigger element
          x = triggerRect.left + triggerRect.width / 2 - tooltipWidth / 2;
          y = triggerRect.top - tooltipHeight - offset;
          break;
        case "bottom":
          // Center the tooltip exactly under the trigger element
          x = triggerRect.left + triggerRect.width / 2 - tooltipWidth / 2;
          y = triggerRect.bottom + offset;
          break;
        case "left":
          x = triggerRect.left - tooltipWidth - offset;
          y = triggerRect.top + triggerRect.height / 2 - tooltipHeight / 2;
          break;
        case "right":
          x = triggerRect.right + offset;
          y = triggerRect.top + triggerRect.height / 2 - tooltipHeight / 2;
          break;
      }

      // Ensure tooltip stays within viewport bounds
      x = Math.max(8, Math.min(x, viewportWidth - tooltipWidth - 8));
      y = Math.max(8, Math.min(y, viewportHeight - tooltipHeight - 8));

      return { position: preferredPosition, adjustedOffset: { x: 0, y: 0 }, x, y };
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [preferredPosition, offset]);

    const updatePosition = useCallback(() => {
      if (isVisible) {
        const newPosition = calculateBestPosition();
        setCalculatedPosition(newPosition);
      }
    }, [isVisible, calculateBestPosition]);

    useEffect(() => {
      if (isVisible) {
        const timeoutId = setTimeout(updatePosition, 0);
        return () => clearTimeout(timeoutId);
      }
    }, [isVisible, updatePosition]);

    useEffect(() => {
      const handleResize = () => {
        if (isVisible) {
          updatePosition();
        }
      };

      const handleScroll = () => {
        if (isVisible) {
          updatePosition();
        }
      };

      window.addEventListener("resize", handleResize);
      window.addEventListener("scroll", handleScroll, true);

      return () => {
        window.removeEventListener("resize", handleResize);
        window.removeEventListener("scroll", handleScroll, true);
      };
    }, [isVisible, updatePosition]);

    const handleMouseEnter = () => {
      if (!hasTooltipText) return;
      setIsVisible(true);
    };

    const handleMouseLeave = () => {
      setIsVisible(false);
    };

    const handleFocus = () => {
      if (!hasTooltipText) return;
      setIsVisible(true);
    };

    const handleBlur = () => {
      setIsVisible(false);
    };

    if (!hasTooltipText) {
      return <>{children}</>;
    }

    return (
      <>
        <span
          ref={triggerRef}
          className={`relative inline-flex items-center ${className}`}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
          onFocus={handleFocus}
          onBlur={handleBlur}
          role='tooltip'
          aria-label={text}
        >
          {children}
        </span>
        {isVisible &&
          createPortal(
            <span
              className={`
                ${getPositionClasses(calculatedPosition.position)}
                opacity-100
              `}
              style={{
                left: `${calculatedPosition.x || 0}px`,
                top: `${calculatedPosition.y || 0}px`,
              }}
            >
              {text}
            </span>,
            document.body,
          )}
      </>
    );
  },
);

Tooltip.displayName = "Tooltip";

export default Tooltip;
