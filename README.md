# Udatracker Starter Code

## Reflection

- **Design decision:** I decided to pass the storage into `OrderTracker` instead of creating it inside the class. This way, in tests I can hand it a fake storage object, and in the real app I hand it the real one. Keeping those two things separate made testing much simpler.

- **Testing insight:** One test required that an invalid status is rejected before the app even checks if the order exists. Without writing that test first, I would have written the code in the wrong order — checking the order first, then the status. The failing test made the right order obvious.

- **Next step:** Right now all data is lost when the server restarts. The clearest next improvement would be saving orders to a real database (like SQLite) so they persist. Because the storage is already separated from the rest of the code, adding that would only require writing a new storage class — nothing else would need to change.

---

This directory contains the starter code for the Udatracker project. The initial structure of directories and files is described below.

```
.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md
```
