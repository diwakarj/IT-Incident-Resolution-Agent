# Workflow — IT Incident Resolution Agent

This describes the conversational branching logic to configure in ElevenLabs'
agent workflow (branching nodes / tool nodes / success-failure routing), not
code. Keep the golden demo path to the VPN/MFA scenario — the rest of the tree
exists so the agent behaves sensibly outside that path, but you don't need to
demo every branch.

```
Employee describes issue
        |
        v
Identify intent / issue category
 (VPN, MFA, Wi-Fi, password, software install, other)
        |
        v
check_known_incidents(issue_category)
        |
   +----+----------------------+
   |                            |
 Known issue found          No known issue
   |                            |
   v                            v
Explain workaround        Ask troubleshooting
   |                       questions (1-2 max)
   v                            |
Did that resolve it?             v
   |            \          Did that resolve it?
  YES            NO             |            \
   |              \            YES            NO
   v               \            |              \
Confirm resolved,    \          v               \
offer anything else   \    Confirm resolved       \
   |                    \   offer anything else     \
   v                      \                          |
 [END - success,           \                         |
  no tool call]              +----------+-------------+
                                          |
                                          v
                              Explain: "I'd like to create
                              an incident and notify support.
                              Priority: [reflects stated
                              urgency]. Is that okay?"
                                          |
                              +-----------+------------+
                              |                        |
                          Confirmed                Declines
                              |                        |
                              v                        v
                     create_incident(...)     Offer fallback contact
                              |                info, end call
                       +------+-------+
                       |              |
                    Success        Failure
                       |              |
                       v              v
              notify_support      Do NOT claim success.
              (auto, part of      Tell employee the system
              create_incident     couldn't be reached, give
              handler)            fallback contact (e.g. IT
                       |           helpdesk phone number).
                       v              |
              Read back incident      v
              number + next steps  [END]
                       |
                       v
              Anything else? -> end call
```

## Notes on the failure branch

This branch is the detail most take-homes skip. It should be visible in the
Loom, even briefly — e.g. by describing it verbally rather than necessarily
demoing a live failure on camera (simulating a dropped webhook mid-recording
is risky for a one-take video). A clean way to show it without risking the
live take: mention it explicitly in the "here's what's happening behind the
scenes" portion of the video, and optionally show a short clip recorded
separately of the failure path, clearly labeled as a supplementary clip
outside the main one-take requirement (check the assignment brief's exact
"one take" wording before doing this — if it's strict, describe it verbally
instead of showing a second clip).

## Escalation

If the employee's issue category isn't in the supported list, or explicitly
asks for a human, skip troubleshooting and go straight to the
confirm-and-create-incident branch, marked as "general escalation" rather than
a specific issue category.
