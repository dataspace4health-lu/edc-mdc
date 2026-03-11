import { ReactNode, useEffect, useRef } from "react";
import { XMarkIcon } from "@heroicons/react/24/solid";
import { twMerge } from "tailwind-merge";

interface FrameProps {
  children: ReactNode;
  open?: boolean;
  onClose: () => void;
  className?: string;
  containerClassName?: string;
}

interface HeadProps {
  children: ReactNode;
  className?: string;
  onClose?: () => void;
}

interface BodyProps {
  children: ReactNode;
  className?: string;
}

export function Frame(props: Readonly<FrameProps>) {
  const { children, open = true, onClose, className, containerClassName } = props;
  const modalRef = useRef(null);
  const containerSizeClassName = containerClassName ?? "w-full max-w-md md:max-w-2xl lg:max-w-4xl";

  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (modalRef.current && modalRef.current == e.target) {
        onClose();
      }
    };

    if (open) {
      document.addEventListener("mousedown", handleOutsideClick);
    } else {
      document.removeEventListener("mousedown", handleOutsideClick);
    }

    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
    };
  }, [open, onClose]);

  return (
    <div
      id='modal'
      ref={modalRef}
      className={`fixed inset-0 p-8 bg-gray-600/60 transition-opacity duration-300 ${
        open ? "opacity-100 visible" : "opacity-0 invisible"
      }`}
      style={{ transition: "opacity 300ms, visibility 300ms", zIndex: 51 }}
    >
      <div
        className={twMerge(
          "relative mx-auto mt-2 transition-transform duration-300 transform",
          containerSizeClassName,
          open ? "scale-100" : "scale-95",
        )}
      >
        <div
          className={`section-lnds-color rounded shadow-xl max-h-[calc(100vh-4rem)] flex flex-col ${className}`}
        >
          {children}
        </div>
      </div>
    </div>
  );
}

const Head = (props: Readonly<HeadProps>) => {
  const { children, className, onClose } = props;
  return (
    <div className='flex justify-between items-center p-4 heading-lnds-color border-b border-lnds-color'>
      <div className={`flex-grow min-w-0 text-lg md:text-xl lg:text-2xl break-all ${className}`}>
        {children}
      </div>
      {onClose && (
        <button onClick={onClose} title='Close' aria-label='Close'>
          <XMarkIcon className='h-7 w-7 mr-1 icon-lnds-color' />
        </button>
      )}
    </div>
  );
};

const Body = (props: Readonly<BodyProps>) => {
  const { children, className } = props;
  return <div className={twMerge("p-6 overflow-y-auto flex-1 min-h-0", className)}>{children}</div>;
};

// eslint-disable-next-line react-refresh/only-export-components
export const Modal = { Frame, Head, Body };
