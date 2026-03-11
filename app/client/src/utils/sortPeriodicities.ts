type Periodicity = {
  value: string;
  eng_label: string;
};

function sortPeriodicities(periodicities: Periodicity[]): Periodicity[] {
  const frequencyWeight: { [key: string]: number } = {
    "http://publications.europa.eu/resource/authority/frequency/ANNUAL": 1,
    "http://publications.europa.eu/resource/authority/frequency/MONTHLY": 2,
    "http://publications.europa.eu/resource/authority/frequency/WEEKLY": 3,
    "http://publications.europa.eu/resource/authority/frequency/DAILY": 4,
    "http://publications.europa.eu/resource/authority/frequency/HOURLY": 5,
    "http://publications.europa.eu/resource/authority/frequency/UPDATE_CONT": 6,
    "http://publications.europa.eu/resource/authority/frequency/QUINQUENNIAL": 7,
    "http://publications.europa.eu/resource/authority/frequency/IRREG": 8,
    "http://publications.europa.eu/resource/authority/frequency/NEVER": 9,
  };

  return periodicities.sort((a, b) => {
    const weightA = frequencyWeight[a.value] || 999;
    const weightB = frequencyWeight[b.value] || 999;

    return weightA - weightB;
  });
}

export default sortPeriodicities;
