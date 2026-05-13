const API_BASE = '/api';

export async function fetchTrips() {
	const res = await fetch(`${API_BASE}/trips/`);
	if (!res.ok) throw new Error('Failed to fetch trips');
	return res.json();
}

export async function fetchTrip(id: number) {
	const res = await fetch(`${API_BASE}/trips/${id}`);
	if (!res.ok) throw new Error('Failed to fetch trip');
	return res.json();
}

export async function createTrip(startedAt: string) {
	const res = await fetch(`${API_BASE}/trips/`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ started_at: startedAt })
	});
	if (!res.ok) throw new Error('Failed to create trip');
	return res.json();
}

export async function addTripPoints(id: number, points: any[]) {
	if (points.length === 0) return { saved: 0 };
	const res = await fetch(`${API_BASE}/trips/${id}/points`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ points })
	});
	if (!res.ok) throw new Error('Failed to save trip points');
	return res.json();
}

export async function stopTrip(id: number, tripData: any) {
	const res = await fetch(`${API_BASE}/trips/${id}/stop`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(tripData)
	});
	if (!res.ok) throw new Error('Failed to stop trip');
	return res.json();
}

export async function saveTrip(tripData: any) {
	const res = await fetch(`${API_BASE}/trips/`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(tripData)
	});
	if (!res.ok) throw new Error('Failed to save trip');
	return res.json();
}

export async function deleteTrip(id: number) {
	const res = await fetch(`${API_BASE}/trips/${id}`, {
		method: 'DELETE'
	});
	if (!res.ok) throw new Error('Failed to delete trip');
	return res.json();
}

export async function fetchStatsSummary() {
	const res = await fetch(`${API_BASE}/stats/summary`);
	if (!res.ok) throw new Error('Failed to fetch stats');
	return res.json();
}
