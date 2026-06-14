'use client';

import { useEffect, useState } from 'react';

type DaySchedule = {
  [department: string]: {
    [day: string]: string;
  };
};

const DAYS = [
  'Montag',
  'Dienstag',
  'Mittwoch',
  'Donnerstag',
  'Freitag',
  'Samstag',
  'Sonntag',
] as const;

export function OpeningHours() {
  const [schedule, setSchedule] = useState<DaySchedule | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/data/opening_hours.json')
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load opening hours');
        return res.json();
      })
      .then((data) => setSchedule(data))
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return (
      <div className="text-muted-foreground text-sm">
        Öffnungszeiten konnten nicht geladen werden.
      </div>
    );
  }

  if (!schedule) {
    return null;
  }

  const formatTimeSlot = (timeSlot: string): string => {
    if (timeSlot === 'geschlossen') {
      return 'Geschlossen';
    }
    if (timeSlot === 'nach Vereinbarung') {
      return 'Nach Vereinbarung';
    }
    // Replace commas with line breaks for multiple time slots
    return timeSlot.replace(/,/g, ', ');
  };

  return (
    <div className="mx-auto w-full max-w-4xl px-4 py-6">
      <h2 className="text-foreground mb-4 text-center text-xl font-semibold">Öffnungszeiten</h2>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {Object.entries(schedule).map(([department, hours]) => (
          <div key={department} className="border-border bg-card rounded-lg border p-4">
            <h3 className="text-foreground mb-3 text-base font-medium">{department}</h3>

            <div className="space-y-1.5">
              {DAYS.map((day) => {
                const timeSlot = hours[day];
                const isToday =
                  new Date().toLocaleDateString('de-DE', { weekday: 'long' }).toLowerCase() ===
                  day.toLowerCase();

                return (
                  <div
                    key={day}
                    className={`flex justify-between text-sm ${
                      isToday ? 'text-foreground font-semibold' : 'text-muted-foreground'
                    }`}
                  >
                    <span className="w-24">{day}:</span>
                    <span className="flex-1 text-right">{formatTimeSlot(timeSlot)}</span>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
