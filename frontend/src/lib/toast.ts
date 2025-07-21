import toast from 'svelte-french-toast';

export const callErrorToast = (message: string) =>
	toast.error(message, {
		position: 'bottom-right',
		className: 'bg-otodb-faint-bg! text-otodb-content-color!'
	});

export const callSuccessToast = (message: string) =>
	toast.success(message, {
		position: 'bottom-right',
		className: 'bg-otodb-faint-bg! text-otodb-content-color!'
	});

export const callInfoToast = (message: string) =>
	toast(message, {
		position: 'bottom-right',
		className: 'bg-otodb-faint-bg! text-otodb-content-color!'
	});
