# Akahu NZ Integration for Home Assistant

This is a custom integration for Home Assistant that connects to the Akahu NZ API. It allows you to view your New Zealand bank account balances and initiate transfers between your accounts.

---
## Installation

### HACS (Home Assistant Community Store)

The easiest way to install is with HACS. If you don't have HACS installed, you can find the installation instructions [here](https://hacs.xyz/).

1.  Open HACS.
2.  Go to **Integrations**.
3.  Click the three dots in the top right and select **Custom repositories**.
4.  Enter the URL to this GitHub repository in the **Repository** field.
5.  Select **Integration** as the category.
6.  Click **Add**.
7.  The Akahu NZ integration will now be available to install.

### Manual Installation

1.  Download the latest release.
2.  Copy the `akahu` directory into your `custom_components` directory in your Home Assistant configuration directory.
3.  Restart Home Assistant.

---
## Configuration

1.  Go to **Settings** -> **Devices & Services**.
2.  Click **Add Integration**.
3.  Search for "Akahu NZ" and select it.
4.  Enter your **Akahu App Token** and **User Token**. You can get these from your Akahu personal app dashboard.
5.  Click **Submit**.

---
## Sensors

This integration will create a sensor for each of your bank accounts. The sensor's state will be the current balance of the account.

The following attributes are also available:

* **account\_type**: The type of account (e.g., "cheque", "savings").
* **available\_balance**: The available balance of the account.
* **institution**: The name of the bank or financial institution.
* **akahuID**: The Akahu ID of the account.
* **status**: The status of the account.
* **formatted\_account\_number**: The formatted account number.

---
## Services

This integration provides two services:

### `akahu.transfer`

This service allows you to initiate a transfer between two of your connected bank accounts.

| Service Data Attribute | Description |
| :--- | :--- |
| `from_account` | The account ID to transfer funds from. |
| `to_account` | The account ID to transfer funds to. |
| `amount` | The amount to transfer. |

### `akahu.refresh`

This service will manually trigger a refresh of the account data from the Akahu API.

---
## Options

You can configure the update interval for the sensors.

1.  Go to **Settings** -> **Devices & Services**.
2.  Find the Akahu NZ integration and click **Configure**.
3.  You can set the **Scan Interval** in minutes. The default is 15 minutes.

[This video](https://www.youtube.com/watch?v=tb1y57asz2I) provides a tutorial on installing HACS and a custom integration.
http://googleusercontent.com/youtube_content/0