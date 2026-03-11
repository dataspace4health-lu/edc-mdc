import { useState, useEffect } from "react";
import { useLoaderData, useOutletContext } from "react-router-dom";
import SearchDataDictionary from "./SearchDataDictionary";
import InsertDataDictionary from "./InsertDataDictionary";
import DataDictionaryTable from "./DataDictionaryTable";
import { fetchDataDictionaries, getDataset } from "./DataDictionaryApi";
import { ResourceDataDictionaryEntry, ResourceDatasetType } from "../../types";
import { usePageTitle } from "../../hooks/usePageTitle";

const DataDictionaryPage = () => {
  const { datasetId } = useLoaderData() as { datasetId: number };

  const { triggerActivityLogRefresh } = useOutletContext() as {
    dataset: ResourceDatasetType;
    triggerActivityLogRefresh: () => void;
  };

  const [dataDictionaries, setDataDictionaries] = useState<ResourceDataDictionaryEntry[]>([]);
  const [dataset, setDataset] = useState<ResourceDatasetType | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [editingEntry, setEditingEntry] = useState<ResourceDataDictionaryEntry | null>(null);

  usePageTitle(dataset ? `${dataset.title} - Data Dictionary` : "Data Dictionary");

  useEffect(() => {
    const loadData = async () => {
      const data = await fetchDataDictionaries(datasetId);
      setDataDictionaries(data);
      const datasetResponse = await getDataset(datasetId);
      setDataset(datasetResponse as ResourceDatasetType);
    };
    loadData();
  }, [datasetId]);

  const handleEntryAdded = (newEntry: ResourceDataDictionaryEntry) => {
    setDataDictionaries((prevEntries) => [...prevEntries, newEntry]);
    setSearchQuery("");
  };

  const handleEntryDeleted = (entryId: number) => {
    setDataDictionaries((prevData) => prevData.filter((entry) => entry.id !== entryId));
    triggerActivityLogRefresh();
  };

  const handleEntryUpdated = (updatedEntry: ResourceDataDictionaryEntry) => {
    setDataDictionaries((prevData) =>
      prevData.map((entry) => (entry.id === updatedEntry.id ? updatedEntry : entry)),
    );
    triggerActivityLogRefresh();
  };

  const handleEditClick = (entry: ResourceDataDictionaryEntry) => {
    setEditingEntry(entry);
  };

  const handleCancelEdit = () => {
    setEditingEntry(null);
  };

  const handleSearchResults = (query: string) => {
    setSearchQuery(query);
  };

  const handleReorderComplete = async () => {
    const data = await fetchDataDictionaries(datasetId);
    setDataDictionaries(data);
  };

  const filteredData = searchQuery
    ? dataDictionaries.filter((entry) =>
        entry.field_name.toLowerCase().includes(searchQuery.toLowerCase()),
      )
    : dataDictionaries;

  const isDuplicate = (fieldName: string, currentEntryId?: number) => {
    if (currentEntryId !== undefined) {
      return dataDictionaries.some(
        (entry) => entry.field_name === fieldName && entry.id !== currentEntryId,
      );
    }
    return dataDictionaries.some((entry) => entry.field_name === fieldName);
  };

  return (
    <div className='flex flex-col w-full space-y-8'>
      <SearchDataDictionary
        onSearchResults={handleSearchResults}
        dataDictionaries={dataDictionaries}
      />
      <InsertDataDictionary
        datasetId={datasetId}
        onEntryAdded={handleEntryAdded}
        onEntryUpdated={handleEntryUpdated}
        isDuplicate={isDuplicate}
        triggerActivityLogRefresh={triggerActivityLogRefresh}
        editingEntry={editingEntry}
        onCancelEdit={handleCancelEdit}
      />
      {dataset && (
        <DataDictionaryTable
          dataset={dataset}
          data={filteredData}
          isEditable={true}
          onDelete={handleEntryDeleted}
          onEdit={handleEditClick}
          triggerActivityLogRefresh={triggerActivityLogRefresh}
          onReorderComplete={handleReorderComplete}
        />
      )}
    </div>
  );
};

export default DataDictionaryPage;
