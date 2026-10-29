export type Day = { date: string; count: number };

export type Alert = {
  level: "danger" | "warning" | "info";
  source: string;
  kind: "streak_ends_today" | "declining" | "flatline" | "projected_stop";
  message: string;
};

export type Summary = {
  current_streak: number;
  longest_streak: number;
  active_today: boolean;
  this_week: number;
  last_week: number;
  change_pct: number | null;
};

export type Dashboard = {
  github: { calendar: Day[]; source: "graphql" | "public_events" } | null;
  leetcode: {
    username: string;
    solved: { all: number; easy: number; medium: number; hard: number };
    calendar: Day[];
  } | null;
  errors: Partial<Record<"github" | "leetcode", string>>;
  alerts: Alert[];
  summaries: Record<string, Summary>;
};

export type Me = {
  login: string;
  avatar_url: string | null;
  leetcode_username: string | null;
  oauth: boolean;
};

export type Goal = {
  id: number;
  title: string;
  daily_target: number;
  today_count: number;
  done_today: boolean;
  streak: number;
  week: boolean[];
};
