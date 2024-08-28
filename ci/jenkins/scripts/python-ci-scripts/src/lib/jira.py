"""This module contains a list of functions related to Jira."""
import logging
import jira
import requests

LOG = logging.getLogger(__name__)


# pylint: disable=too-many-arguments
def create_jira(project, issue_type, summary, description, team_id, labels, priority,
                username, password, extra_values_dict=None):
    """
    Create a Jira ticket.

    Input:
        project: The poject for the Jira ticket (e.g., IDUN)
        issue_type: The type of ticket being created (e.g., Support)
        summary: The title of the ticket
        description: The content of the ticket
        team_id: The team ID of the ticket
        labels: A list of labels to be attached to the ticket - use an empty list for no labels
        priority: The priority of the ticket to be created
        username: The username to connect to Jira
        password: The password to connect to Jira
        extra_values_dict: A dictionary containing any additional information for the ticket

    Output:
        A Jira ticket based on the provided parameters
    """
    jira_connection = jira.JIRA(
        basic_auth=(username, password),
        server="https://eteamproject.internal.ericsson.com/"
    )
    issue_dict = {
        "project": project,
        "issuetype": issue_type,
        "summary": summary,
        "description": description,
        "customfield_18213": {"id": team_id},
        "labels": labels,
        "priority": {"name": priority}
    }
    if extra_values_dict:
        issue_dict.update(extra_values_dict)
    jira_connection.create_issue(fields=issue_dict)


def get_jira_tickets(username, password, **kwargs):
    """
    Get Jira tickets.

    Input:
        username: The username for Jira
        password: The password for Jira
        kwargs: Keyword arguments to filter the tickets (e.g., project="IDUN" will only collect such tickets)

    Returns
    -------
        A dictionary containing information on Jira tickets
    """
    if not kwargs:
        raise Exception("The get_jira_tickets function requires additional arguments to filter tickets")
    jql_query = [f"{key} = {value}" for key, value in kwargs.items()]
    jql_query = " AND ".join(jql_query)
    LOG.info("Filters for collecting Jira tickets: %s", jql_query)
    url = 'https://eteamproject.internal.ericsson.com/rest/api/2/search'
    params = {'jql': jql_query}
    response = requests.get(url, params=params, auth=(username, password), timeout=60)
    return response.json()["issues"]


def remove_duplicate_charts_from_tickets_dict(ticket_list, username, password):
    """
    Remove the duplicate Jira tickets.

    Input:
        ticket_list: The list of charts to be used to create Jira tickets
        username: The username for Jira
        password: The password for Jira

    Returns
    -------
        A dictionary of information on Jira tickets with duplicates removed
    """
    LOG.info("Removing charts that already have an active ticket...")
    ticket_list_without_duplicates = {}
    previous_tickets = get_jira_tickets(username, password, project="IDUN", labels="OUTDATED_IMAGE_TICKET")
    current_tickets = []
    for issue in previous_tickets:
        ticket_status = issue["fields"]["status"]["name"]
        if ticket_status != "Closed":
            chart_name = issue["fields"]["summary"].split(" ")[-1]
            current_tickets.append(chart_name)
    LOG.info("Information on currently open tickets: %s", current_tickets)
    for ticket in ticket_list:
        if ticket not in current_tickets:
            ticket_list_without_duplicates[ticket] = ticket_list[ticket]
        else:
            LOG.info("Removing %s as a ticket for this chart is active", ticket)
    return ticket_list_without_duplicates
