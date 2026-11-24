"""APK/player runtime interface revision. Bump only for incompatible interface changes.

2: the host gained the drawer's frame rate step (jni_android.c's perfPinSet/perfPinGet): the app calls them, so a pack's
runtime has to be rebuilt for the step to exist.
3: the host gained the drawer's motion switches (jni_android.c's motionSet/motionGet): the app calls them from the
drawer's Controls tab, so a pack's runtime has to be rebuilt for the motion to exist.
4: the host gained the drawer's audio output and GPU clock switch (jni_android.c's audioSet/audioGet and
gpuTurboSet/gpuTurboGet): the app calls them, so a pack's runtime has to be rebuilt for them to exist.
5: the host gained the gamepad center's table and the release of every key (jni_android.c's padMapping/padReleaseAll):
the app calls them, so a pack's runtime has to be rebuilt for the center to exist.
6: the host gained the Android game mode (jni_android.c's perfGameMode): the app calls it on every resume, so a
pack's runtime has to be rebuilt for the mode to reach the host.
7: the 0.4.0 base's host (the frame-pacing policy module, the driver quirk table, the regional firmware fonts with
the CJK fallback, multiplayer's per-player input routing): no new JNI surface, but every pack's runtime is rebuilt
so its host is this base's — a pack from 0.3.0 keeps its 0.3.0 host otherwise, and none of the new host reaches it.
8: the app pushes the controller's axis roles and the way it reports its face buttons (twelve axes in the motion
event, RX/RY appended; the pad table's dev line carries ztrig/rxstick and coded): the app sends them, so a pack's
runtime has to be rebuilt for the host to read them — the old host takes ten axes and ignores the new rows, and the
roles stay off without a word.
9: the present path keeps the window texture's bytes when the surface offers only the other sRGB format
(the shader fallback in gfx_vk_present.c): no new JNI surface, but every pack's runtime is rebuilt so the
lighter picture is actually gone after the app update.
10: the host's CPU pin accepts an explicit core list ("cpu:4"), and "big" now means the second-highest
clock tier instead of every core above the lowest one (on the Snapdragon 8 Elite that meant the prime pair
6/7 at 1.0 GHz): no new JNI surface, but every pack's runtime is rebuilt so the new pin is the one that runs.
"""
PLAYER_API_REVISION = 10

# The game profiles the player imports (a package of nxnative/dm/games/<title ID>/ folders) into their own folder: what the package was cut from.
# PROFILES_REVISION counts the syncs of upstream's profiles (1: the first sync, seedds/nxnative at PROFILES_COMMIT); PROFILES_COMMIT is the upstream commit the
# profiles come from. The revision is a label, not a rule: the player imports a package once and keeps it, an app update does not touch it.
PROFILES_REVISION = 1
PROFILES_COMMIT = 'bf1e4edd48b448bbe3f8fadab6a14ff1819ac742'
PROFILES_REPO = 'https://github.com/seedds/nxnative'
