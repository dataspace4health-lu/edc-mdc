export default function PublishedDatasetToastBody() {
  return (
    <div className='mt-2'>
      <div className='relative mb-3 flex justify-center'>
        <div className='h-10 w-10 rounded-full bg-lnds-green/20 animate-pulse' />
        <div className='absolute inset-0 m-auto h-10 w-10 rounded-full border-2 border-lnds-green/30 animate-ping' />
        <div className='absolute -top-1 left-8 h-2 w-2 rounded-full bg-lnds-yellow animate-ping' />
        <div className='absolute top-1 right-8 h-2 w-2 rounded-full bg-lnds-blue animate-ping delay-200' />
        <div className='absolute -bottom-1 left-10 h-2 w-2 rounded-full bg-secondary animate-ping delay-500' />
        <div className='absolute -bottom-1 right-10 h-2 w-2 rounded-full bg-lnds-purple animate-ping delay-700' />
      </div>

      <h4 className='text-lg font-bold text-center'>Congrats, dataset published.</h4>

      <p className='mt-2 text-base font-medium text-center'>
        Your dataset will be live in a few minutes. This is the finish line for this workflow.
      </p>

      <p className='mt-2 text-sm font-medium text-center'>
        Next step: monitor the publication status.
      </p>
    </div>
  );
}
