"""
ThreadManager for managing threads in SUILib.
"""
import threading

import threading

class ManagedThread(threading.Thread):
    """
    Thread class which supports stop_event for cooperative cancellation.
    """
    def __init__(self, target, args=(), kwargs=None):
        """
        Initialize the ManagedThread with a target function and its arguments.
        The target function must accept a 'stop_event' as its first argument.

        Args:
            target (callable): The function to run in the thread.
            args (tuple): Positional arguments to pass to the target function.
            kwargs (dict): Keyword arguments to pass to the target function.
        """
        super().__init__()
        self._stop_event = threading.Event()
        self._target = target
        self._args = args
        self._kwargs = kwargs if kwargs is not None else {}

    def run(self):
        """
        Run the target function with the stop_event and any additional arguments.
        This method is called when the thread is started.
        """
        self._target(self._stop_event, *self._args, **self._kwargs)

    def stop(self):
        """
        Set the stop_event to signal the thread to stop.
        This is a cooperative cancellation mechanism.
        """
        self._stop_event.set()

    def stopped(self):
        """
        Check if the stop_event is set, indicating that the thread should stop.

        Returns:
            bool: True if the stop_event is set, False otherwise.
        """
        return self._stop_event.is_set()

    @property
    def stop_event(self):
        """
        Get the stop_event associated with this thread.
        """
        return self._stop_event

class ThreadManager:
    """
    Singleton class to manage threads in SUILib applications.
    Provides methods to add, remove, list threads, and stop/join all threads.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """
        Create a new instance of ThreadManager if it doesn't exist.
        Ensures that only one instance exists (singleton pattern).
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._threads = set()
            return cls._instance

    def add_thread(self, thread):
        """
        Add a thread to the manager.
        """
        self._threads.add(thread)

    def remove_thread(self, thread):
        """
        Remove a thread from the manager.
        """
        self._threads.discard(thread)

    def list_threads(self):
        """
        List all threads managed by the manager.
        """
        return list(self._threads)

    def run_task(self, task, *args, **kwargs):
        """
        Run a function asynchronously in a new ManagedThread and register it.
        The function must accept 'stop_event' as its first argument.
        When the thread finishes, it's automatically deregistered.

        Args:
            task (callable): The function to run in the thread.
            args (tuple): Positional arguments to pass to the task function.
            kwargs (dict): Keyword arguments to pass to the task function.
    
        Returns:
            ManagedThread: The thread that was created to run the task.

        Example:
            def my_task(stop_event, arg1, arg2):
                while not stop_event.is_set():
                    # Perform some work
                    pass
        """
        manager = self

        def wrapper(stop_event, *args, **kwargs):
            try:
                task(stop_event=stop_event, *args, **kwargs)
            finally:
                manager.remove_thread(threading.current_thread())

        t = ManagedThread(target=wrapper, args=args, kwargs=kwargs)
        self.add_thread(t)
        t.start()
        return t

    def stop_all(self):
        """
        Politely request all managed threads to stop (cooperative cancellation).
        """
        for t in list(self._threads):
            if hasattr(t, 'stop'):
                t.stop()
        for t in list(self._threads):
            t.join()

    def join_all(self):
        """
        Join all managed threads.
        """
        for t in list(self._threads):
            t.join()

    @classmethod
    def instance(cls):
        """
        Get the singleton instance of ThreadManager.
        If it doesn't exist, create it.
        """
        return cls()