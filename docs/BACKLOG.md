# Backlog

Domain changes agreed on but not scheduled yet. Each item says why it is
needed and what it touches; move it to a plan in `sdd/plans/` when it is picked
up.

## Reservations

### Privacy for meetings

Meetings (`reservation.type = MEETING`) can be internal (department councils,
student group meetings) and should not be public by default. Today the public
search works around it by indexing only meetings whose title mentions
"monitoria" (see `docs/SEARCH.md`), and other public screens (the public room
map) still show every meeting.

Needed: an explicit visibility on the reservation (e.g. `public` / `private`,
defaulting to private for meetings), respected by every public endpoint, the
room map and the search index. The meeting `link` should follow the same rule.

### `monitoria` table

Monitorias are booked today as events or as meetings, and are only recognized
by their title. They should be their own reservation child, like an exam:

- references a subject and, optionally, classes (like `exam` + `examclasslink`);
- possibly the monitor(s) responsible;
- a new `ReservationType.MONITORING` and its child table, with a migration that
  moves existing events/meetings titled "Monitoria …" into it.

The search index then gets a `monitoring` document type linked to the subject
and classes, instead of the title heuristic.

### Person responsible for a reservation

Some reservations need a responsible person who is not the user who booked
it. Example: extension groups (grupos de extensão) must name a professor as
responsible. A reservation should accept a responsible person, either a user
(`responsible_id`) or a free-text name for people without an account.

### Integrity: every reservation has exactly one matching child

A reservation is specialized by exactly one child row matching its type
(`exam`, `event` or `meeting`). Until 2025-11-02 (commit 7df2f93) creating a
solicitation did not create the child; nine meetings were left without one and
were backfilled by migration `3b9d7e5a1c24`. Today nothing in the database
prevents this from happening again.

Needed: enforce the invariant in the database, e.g. a deferrable constraint
trigger checked at commit time (reservation has the child for its type and no
other), after confirming every code path creates the reservation and its child
in the same transaction.
