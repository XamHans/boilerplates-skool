'use client';

import { useEffect, useState } from 'react';
import { ChevronDown, ChevronUp, Clock } from 'lucide-react';

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

export function CompactOpeningHours() {
  const [schedule, setSchedule] = useState<DaySchedule | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    fetch('/data/opening_hours.json')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => setSchedule(data))
      .catch(() => setSchedule(null));
  }, []);

  if (!schedule) return null;

  const today = new Date().toLocaleDateString('de-DE', { weekday: 'long' });
  const todayIndex = DAYS.findIndex((day) => day.toLowerCase() === today.toLowerCase());

  const formatTime = (time: string) => {
    if (time === 'geschlossen') return 'Geschlossen';
    if (time === 'nach Vereinbarung') return 'N. Vereinb.';
    return time;
  };

  return (
    <div className="bg-card/95 border-border rounded-lg border shadow-sm backdrop-blur">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="hover:bg-accent/50 flex w-full items-center justify-between px-3 py-2 text-left transition-colors"
      >
        <div className="flex items-center gap-2">
          <Clock className="text-muted-foreground h-4 w-4" />
          <span className="text-sm font-medium">Öffnungszeiten</span>
        </div>
        {isExpanded ? (
          <ChevronUp className="text-muted-foreground h-4 w-4" />
        ) : (
          <ChevronDown className="text-muted-foreground h-4 w-4" />
        )}
      </button>

      {isExpanded ? (
        <div className="border-border space-y-3 border-t px-3 py-3">
          {Object.entries(schedule).map(([dept, hours]) => (
            <div key={dept} className="space-y-1">
              <div className="text-muted-foreground text-xs font-medium">{dept}</div>
              <div className="space-y-0.5">
                {DAYS.map((day, idx) => (
                  <div
                    key={day}
                    className={`flex justify-between text-xs ${
                      idx === todayIndex ? 'font-semibold' : 'text-muted-foreground'
                    }`}
                  >
                    <span className="w-20">{day}:</span>
                    <span className="text-right">{formatTime(hours[day])}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="px-3 pb-2">
          {Object.entries(schedule).map(([dept, hours]) => {
            const todayHours = hours[DAYS[todayIndex]] || 'N/A';
            return (
              <div key={dept} className="flex items-baseline justify-between gap-2 text-xs">
                <span className="text-muted-foreground">{dept}:</span>
                <span className="font-medium">{formatTime(todayHours)}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
