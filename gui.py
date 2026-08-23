import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from datetime import datetime

from filter import (
    get_active_jobs,
    get_older_jobs,
    get_applied_jobs,
    mark_job_applied,
    mark_job_unapplied,
)


# Application settings


WINDOW_TITLE = "Job Finder"

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800


# Helper functions


def format_date(date_string):

    if not date_string:
        return "Unknown"

    try:

        date = datetime.fromisoformat(
            date_string
        )

        return date.strftime(
            "%b %d, %Y %I:%M %p"
        )

    except (ValueError, TypeError):

        return date_string


def shorten_text(text, max_length=100):

    if not text:
        return ""

    text = str(text).replace(
        "\n",
        " "
    ).strip()

    if len(text) <= max_length:
        return text

    return text[:max_length - 3] + "..."


# Main app


class JobFinderApp(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title(
            WINDOW_TITLE
        )

        self.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )

        self.minsize(
            1000,
            650
        )

        self.jobs = []

        self.current_job = None

        self.sort_order = "newest"

        self.current_section = "active"

        self.create_styles()

        self.create_widgets()

        self.load_jobs()


    # Styles

    def create_styles(self):

        style = ttk.Style(self)

        try:

            style.theme_use(
                "clam"
            )

        except tk.TclError:

            pass

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 16, "bold")
        )

        style.configure(
            "JobTitle.TLabel",
            font=("Segoe UI", 14, "bold")
        )

        style.configure(
            "Normal.TLabel",
            font=("Segoe UI", 10)
        )


    # Build interface

    def create_widgets(self):


        top_frame = ttk.Frame(
            self,
            padding=(15, 12)
        )

        top_frame.pack(
            fill="x"
        )

        ttk.Label(
            top_frame,
            text="Job Finder",
            style="Title.TLabel"
        ).pack(
            side="left"
        )

        self.count_label = ttk.Label(
            top_frame,
            text="",
            style="Normal.TLabel"
        )

        self.count_label.pack(
            side="left",
            padx=(20, 0)
        )

        ttk.Button(
            top_frame,
            text="Refresh",
            command=self.load_jobs
        ).pack(
            side="right"
        )

        # Search and sorting

        controls_frame = ttk.Frame(
            self,
            padding=(15, 0, 15, 10)
        )

        controls_frame.pack(
            fill="x"
        )

        ttk.Label(
            controls_frame,
            text="Search:"
        ).pack(
            side="left"
        )

        self.search_var = tk.StringVar()

        self.search_entry = ttk.Entry(
            controls_frame,
            textvariable=self.search_var,
            width=40
        )

        self.search_entry.pack(
            side="left",
            padx=(8, 8)
        )

        self.search_entry.bind(
            "<Return>",
            lambda event: self.load_jobs()
        )

        ttk.Button(
            controls_frame,
            text="Search",
            command=self.load_jobs
        ).pack(
            side="left"
        )

        ttk.Button(
            controls_frame,
            text="Clear",
            command=self.clear_search
        ).pack(
            side="left",
            padx=(5, 20)
        )

        ttk.Label(
            controls_frame,
            text="Sort:"
        ).pack(
            side="left"
        )

        self.sort_var = tk.StringVar(
            value="Newest first"
        )

        sort_dropdown = ttk.Combobox(
            controls_frame,
            textvariable=self.sort_var,
            values=[
                "Newest first",
                "Oldest first",
                "Location"
            ],
            state="readonly",
            width=15
        )

        sort_dropdown.pack(
            side="left",
            padx=(8, 0)
        )

        sort_dropdown.bind(
            "<<ComboboxSelected>>",
            self.sort_changed
        )

        # Notebook / sections

        self.notebook = ttk.Notebook(
            self
        )

        self.notebook.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        self.active_tab = ttk.Frame(
            self.notebook,
            padding=8
        )

        self.applied_tab = ttk.Frame(
            self.notebook,
            padding=8
        )

        self.older_tab = ttk.Frame(
            self.notebook,
            padding=8
        )

        self.notebook.add(
            self.active_tab,
            text="Active Jobs"
        )

        self.notebook.add(
            self.applied_tab,
            text="Applied Jobs"
        )

        self.notebook.add(
            self.older_tab,
            text="Older Jobs"
        )

        self.notebook.bind(
            "<<NotebookTabChanged>>",
            self.section_changed
        )

        self.create_job_section(
            self.active_tab
        )

        self.create_job_section(
            self.applied_tab
        )

        self.create_job_section(
            self.older_tab
        )

    # Create job section

    def create_job_section(self, parent):

        main_frame = ttk.Frame(
            parent
        )

        main_frame.pack(
            fill="both",
            expand=True
        )

        # Left side

        list_frame = ttk.LabelFrame(
            main_frame,
            text="Jobs",
            padding=8
        )

        list_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        columns = (
            "date",
            "title",
            "company",
            "location",
            "source"
        )

        tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        tree.heading(
            "date",
            text="Date"
        )

        tree.heading(
            "title",
            text="Job Title"
        )

        tree.heading(
            "company",
            text="Company"
        )

        tree.heading(
            "location",
            text="Location"
        )

        tree.heading(
            "source",
            text="Source"
        )

        tree.column(
            "date",
            width=145,
            minwidth=100
        )

        tree.column(
            "title",
            width=320,
            minwidth=200
        )

        tree.column(
            "company",
            width=180,
            minwidth=100
        )

        tree.column(
            "location",
            width=180,
            minwidth=100
        )

        tree.column(
            "source",
            width=160,
            minwidth=100
        )

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=tree.yview
        )

        tree.configure(
            yscrollcommand=scrollbar.set
        )

        tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        tree.bind(
            "<<TreeviewSelect>>",
            self.job_selected
        )

        # Store tree by section

        if parent == self.active_tab:

            self.active_tree = tree

        elif parent == self.applied_tab:

            self.applied_tree = tree

        else:

            self.older_tree = tree

        # Right side

        detail_frame = ttk.LabelFrame(
            main_frame,
            text="Job Details",
            padding=15
        )

        detail_frame.pack(
            side="right",
            fill="both",
            expand=True,
            padx=(10, 0)
        )

        # Title

        title_label = ttk.Label(
            detail_frame,
            text="Select a job",
            style="JobTitle.TLabel",
            wraplength=450
        )

        title_label.pack(
            anchor="w",
            fill="x"
        )

        # Company

        company_label = ttk.Label(
            detail_frame,
            text="",
            style="Normal.TLabel"
        )

        company_label.pack(
            anchor="w",
            pady=(10, 0)
        )

        # Location

        location_label = ttk.Label(
            detail_frame,
            text="",
            style="Normal.TLabel"
        )

        location_label.pack(
            anchor="w",
            pady=(4, 0)
        )

        # Date

        date_label = ttk.Label(
            detail_frame,
            text="",
            style="Normal.TLabel"
        )

        date_label.pack(
            anchor="w",
            pady=(4, 0)
        )

        # Source

        source_label = ttk.Label(
            detail_frame,
            text="",
            style="Normal.TLabel"
        )

        source_label.pack(
            anchor="w",
            pady=(4, 0)
        )

        # Separator

        ttk.Separator(
            detail_frame,
            orient="horizontal"
        ).pack(
            fill="x",
            pady=15
        )

        # Buttons

        button_frame = ttk.Frame(
            detail_frame
        )

        button_frame.pack(
            fill="x",
            pady=(0, 12)
        )

        open_button = ttk.Button(
            button_frame,
            text="Open Job Posting",
            command=self.open_job,
            state="disabled"
        )

        open_button.pack(
            side="left"
        )

        applied_button = ttk.Button(
            button_frame,
            text="Mark Applied",
            command=self.toggle_applied,
            state="disabled"
        )

        applied_button.pack(
            side="left",
            padx=(8, 0)
        )

        # Description

        description_label = ttk.Label(
            detail_frame,
            text="Description:",
            style="Normal.TLabel"
        )

        description_label.pack(
            anchor="w",
            pady=(0, 5)
        )

        description_frame = ttk.Frame(
            detail_frame
        )

        description_frame.pack(
            fill="both",
            expand=True
        )

        description_text = tk.Text(
            description_frame,
            wrap="word",
            font=("Segoe UI", 10),
            padx=8,
            pady=8,
            relief="flat",
            background="#f5f5f5"
        )

        description_scrollbar = ttk.Scrollbar(
            description_frame,
            orient="vertical",
            command=description_text.yview
        )

        description_text.configure(
            yscrollcommand=description_scrollbar.set
        )

        description_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        description_scrollbar.pack(
            side="right",
            fill="y"
        )

        description_text.configure(
            state="disabled"
        )

        # Store detail widgets

        section_widgets = {
            "title": title_label,
            "company": company_label,
            "location": location_label,
            "date": date_label,
            "source": source_label,
            "description": description_text,
            "open": open_button,
            "applied": applied_button,
        }

        if parent == self.active_tab:

            self.active_details = section_widgets

        elif parent == self.applied_tab:

            self.applied_details = section_widgets

        else:

            self.older_details = section_widgets


    # Current section

    def get_current_tree(self):

        if self.current_section == "active":

            return self.active_tree

        if self.current_section == "applied":

            return self.applied_tree

        return self.older_tree


    def get_current_details(self):

        if self.current_section == "active":

            return self.active_details

        if self.current_section == "applied":

            return self.applied_details

        return self.older_details


    # Load jobs

    def load_jobs(self):

        search_text = (
            self.search_var.get()
            .strip()
        )

        keywords = None

        if search_text:

            keywords = [
                word
                for word in search_text.split()
                if word
            ]

        try:

            self.active_jobs = get_active_jobs(
                keywords=keywords,
                sort_order=self.sort_order
            )

            self.applied_jobs = get_applied_jobs(
                keywords=keywords,
                sort_order=self.sort_order
            )

            self.older_jobs = get_older_jobs(
                keywords=keywords,
                sort_order=self.sort_order
            )

        except sqlite3.Error as error:

            messagebox.showerror(
                "Database Error",
                f"Could not read jobs.db.\n\n{error}"
            )

            return

        self.populate_tree(
            self.active_tree,
            self.active_jobs
        )

        self.populate_tree(
            self.applied_tree,
            self.applied_jobs
        )

        self.populate_tree(
            self.older_tree,
            self.older_jobs
        )

        self.update_tab_counts()

        self.clear_details()


    # Populate tree

    def populate_tree(
        self,
        tree,
        jobs
    ):

        for item in tree.get_children():

            tree.delete(
                item
            )

        for job in jobs:

            tree.insert(
                "",
                "end",
                iid=str(job["id"]),
                values=(
                    format_date(
                        job["published"]
                    ),
                    shorten_text(
                        job["title"],
                        80
                    ),
                    shorten_text(
                        job["company"],
                        40
                    ),
                    shorten_text(
                        job["location"],
                        40
                    ),
                    job["source"] or ""
                )
            )


    # Tab counts

    def update_tab_counts(self):

        active_count = len(
            self.active_jobs
        )

        applied_count = len(
            self.applied_jobs
        )

        older_count = len(
            self.older_jobs
        )

        self.notebook.tab(
            self.active_tab,
            text=f"Active Jobs ({active_count})"
        )

        self.notebook.tab(
            self.applied_tab,
            text=f"Applied Jobs ({applied_count})"
        )

        self.notebook.tab(
            self.older_tab,
            text=f"Older Jobs ({older_count})"
        )

        self.count_label.config(
            text=(
                f"Active: {active_count}   "
                f"Applied: {applied_count}   "
                f"Older: {older_count}"
            )
        )


    # Search

    def clear_search(self):

        self.search_var.set("")

        self.load_jobs()

        self.search_entry.focus()


    # Sort

    def sort_changed(self, event=None):

        selected = self.sort_var.get()

        if selected == "Oldest first":

            self.sort_order = "oldest"

        elif selected == "Location":

            self.sort_order = "location"

        else:

            self.sort_order = "newest"

        self.load_jobs()


    # Section changed

    def section_changed(self, event=None):

        index = self.notebook.index(
            self.notebook.select()
        )

        if index == 0:

            self.current_section = "active"

        elif index == 1:

            self.current_section = "applied"

        else:

            self.current_section = "older"

        self.clear_details()


    # Job selected

    def job_selected(self, event=None):

        tree = self.get_current_tree()

        selection = tree.selection()

        if not selection:
            return

        job_id = int(
            selection[0]
        )

        if self.current_section == "active":

            jobs = self.active_jobs

        elif self.current_section == "applied":

            jobs = self.applied_jobs

        else:

            jobs = self.older_jobs

        job = None

        for item in jobs:

            if item["id"] == job_id:

                job = item

                break

        if job is None:
            return

        self.current_job = job

        self.show_job(
            job
        )


    # Show details

    def show_job(self, job):

        details = self.get_current_details()

        title = (
            job["title"]
            or "Untitled"
        )

        company = (
            job["company"]
            or "Unknown"
        )

        location = (
            job["location"]
            or "Not specified"
        )

        source = (
            job["source"]
            or "Unknown"
        )

        published = format_date(
            job["published"]
        )

        details["title"].config(
            text=title
        )

        details["company"].config(
            text=f"Company: {company}"
        )

        details["location"].config(
            text=f"Location: {location}"
        )

        details["date"].config(
            text=f"Published: {published}"
        )

        details["source"].config(
            text=f"Source: {source}"
        )

        # Description

        description = (
            job["description"]
            or "No description available."
        )

        details["description"].configure(
            state="normal"
        )

        details["description"].delete(
            "1.0",
            "end"
        )

        details["description"].insert(
            "1.0",
            description
        )

        details["description"].configure(
            state="disabled"
        )

        # Job Posting button

        if job["url"]:

            details["open"].configure(
                state="normal"
            )

        else:

            details["open"].configure(
                state="disabled"
            )

        # Applied button

        if self.current_section == "applied":

            details["applied"].configure(
                text="Mark Unapplied",
                state="normal"
            )

        else:

            details["applied"].configure(
                text="Mark Applied",
                state="normal"
            )


    # Clear details

    def clear_details(self):

        self.current_job = None

        for details in (
            self.active_details,
            self.applied_details,
            self.older_details
        ):

            details["title"].config(
                text="Select a job"
            )

            details["company"].config(
                text=""
            )

            details["location"].config(
                text=""
            )

            details["date"].config(
                text=""
            )

            details["source"].config(
                text=""
            )

            details["description"].configure(
                state="normal"
            )

            details["description"].delete(
                "1.0",
                "end"
            )

            details["description"].configure(
                state="disabled"
            )

            details["open"].configure(
                state="disabled"
            )

            details["applied"].configure(
                state="disabled"
            )


    # Mark applied / unapplied

    def toggle_applied(self):

        if not self.current_job:
            return

        job_id = self.current_job["id"]

        try:

            if self.current_section == "applied":

                mark_job_unapplied(
                    job_id
                )

            else:

                mark_job_applied(
                    job_id
                )

        except sqlite3.Error as error:

            messagebox.showerror(
                "Database Error",
                f"Could not update job.\n\n{error}"
            )

            return

        self.load_jobs()


    # Open job posting

    def open_job(self):

        if not self.current_job:
            return

        url = self.current_job["url"]

        if not url:
            return

        webbrowser.open(
            url
        )


# Start application

if __name__ == "__main__":

    app = JobFinderApp()

    app.mainloop()