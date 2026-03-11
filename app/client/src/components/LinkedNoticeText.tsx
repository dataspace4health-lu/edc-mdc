import { ReactNode } from "react";

type LinkedNoticeTextProps = {
  message: string;
};

const LinkedNoticeText = ({ message }: LinkedNoticeTextProps) => {
  return <>{parseMarkdownLinks(message)}</>;
};

function parseMarkdownLinks(message: string): ReactNode[] {
  const linkPattern = /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g;
  const segments: ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let key = 0;

  while ((match = linkPattern.exec(message)) !== null) {
    if (match.index > lastIndex) {
      segments.push(message.slice(lastIndex, match.index));
    }

    const [, text, url] = match;
    segments.push(
      <a
        key={`linked-notice-text-${key++}`}
        href={url}
        target='_blank'
        rel='noreferrer noopener'
        className='underline text-lnds-blue hover:text-lnds-dark-blue'
      >
        {text}
      </a>,
    );
    lastIndex = linkPattern.lastIndex;
  }

  if (lastIndex < message.length) {
    segments.push(message.slice(lastIndex));
  }

  return segments;
}

export default LinkedNoticeText;
