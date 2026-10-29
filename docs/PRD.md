# PRD: DevBoard

## Problem

A developer's practice habits are split across GitHub, LeetCode and private to-do lists. Each shows a number for today, but none says "you're slowing down". By the time a streak breaks, it's too late.

## Goal

One page that shows all three sources and warns **before** a streak breaks, based on the trend rather than a single day.

## Users

Students and early-career developers who keep up a daily coding habit for interviews or open source.

## User stories

| As a… | I want to… | So that… |
|---|---|---|
| developer | log in with GitHub | my contribution calendar loads without typing anything |
| developer | add my LeetCode username | solves show next to commits |
| developer | see a banner when my streak ends tonight | I can still save it |
| developer | see when activity drops week-over-week | I notice a slump early |
| developer | set daily goals with a target count | I can track habits GitHub and LeetCode don't cover |
| developer | dismiss a warning for today | it doesn't nag me after I've seen it |

## Requirements

- GitHub OAuth login; a dev-only login by username for local use
- GitHub contribution calendar (365 days with OAuth, public pushes otherwise)
- LeetCode solved counts by difficulty and a submission calendar
- Goals: create, rename, delete, log +/− for today, 7-day history, streak
- Risk rules: streak ends today, week-over-week decline, flatline, projected stop
- Goals persist in PostgreSQL across sessions
- Works on phone-width screens

## Non-goals

- Writing to GitHub or LeetCode
- Notifications outside the app (email, push)
- Multi-user teams or leaderboards
- Storing long-term history of GitHub/LeetCode data (v2)

## Success criteria

- The dashboard loads with both sources in one request; one failing source still renders the rest
- Every risk rule is covered by a unit test

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
