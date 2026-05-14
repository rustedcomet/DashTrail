export const APP_TIME_ZONE = 'America/Panama';

export function parseUtcDate(value: string | null | undefined): Date | null {
	if (!value) return null;
	const normalized = /(?:Z|[+-]\d{2}:?\d{2})$/.test(value) ? value : `${value}Z`;
	const date = new Date(normalized);
	return Number.isNaN(date.getTime()) ? null : date;
}

export function formatDate(value: string | null | undefined) {
	const date = parseUtcDate(value);
	if (!date) return 'Unavailable';
	return new Intl.DateTimeFormat(undefined, {
		timeZone: APP_TIME_ZONE,
		year: 'numeric',
		month: 'numeric',
		day: 'numeric'
	}).format(date);
}

export function formatTime(value: string | null | undefined) {
	const date = parseUtcDate(value);
	if (!date) return 'Unavailable';
	return new Intl.DateTimeFormat(undefined, {
		timeZone: APP_TIME_ZONE,
		hour: '2-digit',
		minute: '2-digit'
	}).format(date);
}
