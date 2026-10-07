# VPN Troubleshooting

## Known active incident: MFA-linked VPN authentication failures
Status: Active (use this for the golden demo path)
Summary: Employees connecting to the corporate VPN may see "Authentication
failed" even with correct credentials. Root cause is a delay in MFA push
notification delivery for the mobile authenticator app.

Workaround:
1. Close the VPN client fully (not just disconnect).
2. Open the mobile authenticator app manually and generate a fresh code.
3. Reopen the VPN client and enter the code manually instead of waiting for
   the push notification.

If the workaround does not resolve the issue within one retry, this should be
escalated as a P2 incident, since it blocks normal work access.

## General VPN connection issues (no known incident)
Common causes, in order of likelihood:
1. Expired VPN client — check for a pending update in the software center.
2. Incorrect server region selected — should match the employee's home
   office region.
3. Local network blocking VPN ports — try a different network (e.g. mobile
   hotspot) to isolate.
4. Corrupted local VPN profile — may require IT to re-provision the profile.

If none of the above resolves it and there's no known incident, create a
standard-priority incident with the specific error message reported.
