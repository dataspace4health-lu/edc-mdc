import { type ComponentType, type SVGProps } from "react";

interface IconListProps {
  items: string[];
  Icon: ComponentType<SVGProps<SVGSVGElement>>;
  getHref?: (item: string, index: number) => string | undefined;
  openInNewTab?: boolean;
  linkClassName?: string;
  itemClassName?: string;
  iconClassName?: string;
}

const IconList = (props: Readonly<IconListProps>) => {
  const {
    items,
    Icon,
    getHref,
    openInNewTab = false,
    linkClassName = "text-lnds-color underline break-all hover:text-lnds-dark-blue",
    itemClassName = "text-lnds-color break-all",
    iconClassName = "h-5 w-5 label-lnds-color mr-1 flex-shrink-0",
  } = props;

  return (
    <div className='flex flex-col gap-1'>
      {items.map((item, index) => {
        const href = getHref ? getHref(item, index) : undefined;

        return (
          <div key={`${item}-${index}`} className='flex items-center'>
            <Icon className={iconClassName} />
            {href ? (
              <a
                href={href}
                target={openInNewTab ? "_blank" : undefined}
                rel={openInNewTab ? "noopener noreferrer" : undefined}
                className={linkClassName}
              >
                {item}
              </a>
            ) : (
              <span className={itemClassName}>{item}</span>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default IconList;
