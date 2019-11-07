
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2018 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

# modified by Alex
# see https://github.com/aforren1/psychopy/blob/d434ec48ec1e7791a0a0a18a20165f1c2bb2e5a2/psychopy/platform_specific/linux.py
import os
import sys
import gc

if sys.platform == 'win32':
    try:
        from ctypes import WinDLL, get_last_error, set_last_error
        windll = WinDLL('kernel32', use_last_error=True)
        importWindllFailed = False
    except Exception:
        importWindllFailed = True

    FALSE = 0

    PROCESS_SET_INFORMATION = 0x0200
    PROCESS_QUERY_INFORMATION = 0x0400

    NORMAL_PRIORITY_CLASS = 32
    HIGH_PRIORITY_CLASS = 128
    REALTIME_PRIORITY_CLASS = 256
    THREAD_PRIORITY_NORMAL = 0
    THREAD_PRIORITY_HIGHEST = 2
    THREAD_PRIORITY_TIME_CRITICAL = 15

    # sleep signals
    ES_CONTINUOUS = 0x80000000
    ES_DISPLAY_REQUIRED = 0x00000002
    ES_SYSTEM_REQUIRED = 0x00000001

    def rush(enable=True, realtime=False):
        """Raise the priority of the current thread/process.
        Set with rush(True) or rush(False)
        Beware and don't take priority until after debugging your code
        and ensuring you have a way out (e.g. an escape sequence of
        keys within the display loop). Otherwise you could end up locked
        out and having to reboot!
        """
        if enable:
            gc.disable()
        else:
            gc.enable()
        if importWindllFailed:
            return False

        pr_rights = PROCESS_QUERY_INFORMATION | PROCESS_SET_INFORMATION
        pr = windll.OpenProcess(pr_rights, FALSE, os.getpid())
        thr = windll.GetCurrentThread()

        if enable:
            if realtime:
                windll.SetPriorityClass(pr, REALTIME_PRIORITY_CLASS)
                windll.SetThreadPriority(thr, THREAD_PRIORITY_TIME_CRITICAL)
            else:
                windll.SetPriorityClass(pr, HIGH_PRIORITY_CLASS)
                windll.SetThreadPriority(thr, THREAD_PRIORITY_HIGHEST)
        else:
            windll.SetPriorityClass(pr, NORMAL_PRIORITY_CLASS)
            windll.SetThreadPriority(thr, THREAD_PRIORITY_NORMAL)
        err = get_last_error()
        if err:
            set_last_error(0)
            return False
        return True

elif sys.platform == 'darwin':
    def rush(value=True):
        pass
else:  # linux
    try:
        import ctypes
        import ctypes.util
        c = ctypes.cdll.LoadLibrary(ctypes.util.find_library('c'))
        importCtypesFailed = False
    except Exception:
        importCtypesFailed = True

    # FIFO and RR(round-robin) allow highest priority for realtime
    SCHED_NORMAL = 0
    SCHED_FIFO = 1
    SCHED_RR = 2
    SCHED_BATCH = 3

    if not importCtypesFailed:
        class _SchedParams(ctypes.Structure):
            _fields_ = [('sched_priority', ctypes.c_int)]

    def rush(enable=True):
        """Raise the priority of the current thread/process using
            - sched_setscheduler
        realtime arg is not used in Linux implementation.
        NB for rush() to work on (debian-based?) Linux requires that the
        script is run using a copy of python that is allowed to change
        priority, eg: sudo setcap cap_sys_nice=eip <sys.executable>,
        and maybe restart PsychoPy. If <sys.executable> is the system python,
        it's important to restore it back to normal to avoid possible
        side-effects. Alternatively, use a different python executable,
        and change its cap_sys_nice.
        """
        if enable:
            gc.disable()
            sched_type = SCHED_RR
            sched_val = c.sched_get_priority_max(sched_type)
        else:
            gc.enable()
            sched_type = SCHED_NORMAL
            sched_val = c.sched_get_priority_min(sched_type)
        if importCtypesFailed:
            return False
        schedParams = _SchedParams()
        schedParams.sched_priority = sched_val
        err = c.sched_setscheduler(0, sched_type, ctypes.byref(schedParams))
        if err == -1:
            return False
        return True
