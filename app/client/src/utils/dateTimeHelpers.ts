import { formatInTimeZone, toZonedTime } from "date-fns-tz";
import { startOfDay, startOfToday, isEqual, differenceInMilliseconds } from "date-fns";

const DEFAULT_DATE_FORMAT = "d MMMM yyyy";
const DEFAULT_DATETIME_FORMAT = "d MMMM yyyy, HH.mm (zzz)";
const DEFAULT_TIME_FORMAT = "HH.mm (zzz)";
const LOCAL_TIMEZONE = Intl.DateTimeFormat().resolvedOptions().timeZone;

function ISOToYMD(iso: string) {
  return iso.slice(0, 10);
}

function toYMD(date: Date) {
  return ISOToYMD(date.toISOString());
}

function nowISO() {
  return new Date().toISOString();
}

function nowYMD() {
  return ISOToYMD(nowISO());
}

const formatDate = (date: string | null, formatStr = DEFAULT_DATE_FORMAT) => {
  if (!date) {
    return undefined;
  }
  return formatInTimeZone(date, LOCAL_TIMEZONE, formatStr);
};

const formatDateTime = (dateTime: string | null, formatStr = DEFAULT_DATETIME_FORMAT) => {
  if (!dateTime) {
    return undefined;
  }
  return formatInTimeZone(dateTime, LOCAL_TIMEZONE, formatStr);
};

const formatTime = (time: string | null, formatStr = DEFAULT_TIME_FORMAT) => {
  if (!time) {
    return undefined;
  }
  return formatInTimeZone(time, LOCAL_TIMEZONE, formatStr);
};

const getStartOfDay = (date: string | Date): Date => {
  return startOfDay(toZonedTime(date, LOCAL_TIMEZONE));
};
const getStartOfToday = (): Date => {
  return startOfToday();
};

const areDatesEqual = (date1: Date | string, date2: Date | string): boolean => {
  return isEqual(date1, date2);
};

const diff = (date1: Date | string, date2: Date | string): number => {
  return differenceInMilliseconds(date1, date2);
};

const formatRelativeTime = (dateString: string) => {
  const now = new Date();
  const date = new Date(dateString);
  const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

  if (diffInDays === 0) return "Today";
  if (diffInDays === 1) return "Yesterday";
  if (diffInDays < 30) return `${diffInDays} days ago`;
  if (diffInDays < 365) return `${Math.floor(diffInDays / 30)} months ago`;
  return `${Math.floor(diffInDays / 365)} years ago`;
};

export const DateUtils = {
  toYMD,
  nowISO,
  nowYMD,
  formatDate,
  formatDateTime,
  formatTime,
  formatRelativeTime,
  getStartOfDay,
  getStartOfToday,
  areDatesEqual,
  diff,
};
