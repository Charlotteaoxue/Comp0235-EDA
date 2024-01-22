
# README

The aim of this project is to build a distributed protein structure prediction system for a biochemistry research team at the UCL School of Medicine. The team has developed a data analysis process that can predict the 3D structure of proteins in the human genome, but its performance is limited by computational efficiency. To overcome this challenge, I have designed a system that will be deployed on six cloud computers and employ Ansible as a configuration management tool to optimise the data processing flow. In addition, the system will utilise Prometheus and Grafana to provide visualisation for monitoring and logging. This system is designed to significantly improve the speed and efficiency of protein structure prediction, thereby aiding the advancement of biomedical research.


## Usage Instructions

### Configure Inventory File

```bash
touch <your inventory file name>
vi <your inventory file name>
```

**1.Define the Control Node**

In the inventory file, first add the IP address of the controlled machine

```plaintext
[control]
my_control ansible_host=xx.xx.xx.xx
```

**2.Define the Client Node1**

Next, define the client machine that will be managed by the control machine

```plaintext
[client]
my_client ansible_host = xx.xx.xx.xx
```

**3.Define the cluster nodes**

```plaintext
[cluster]
cluster1 ansible_host = xx.xx.xx.xx
cluster2 ansible_host = xx.xx.xx.xx
cluster3 ansible_host = xx.xx.xx.xx
cluster4 ansible_host = xx.xx.xx.xx
<You can add more cluster machines>
```

**4.Define Common Variables for All Hosts**

```plaintext
[all:vars]
ansible_user = <Fill in your user role]>
ansible_ssh_private_key_file = <Fill in your private key path>
region = <region code>
```

## Run the Playbook

### Data Pipeline

**1.Navigate to the Playbook Directory**

Ensure you are in the directory where your_playbook.yaml is located

You can use the cd command to change directories, if necessary

```bash
cd /path/to/your/playbook/directory
```

**2.Execute the Playbook**

Before executing the playbook, ensure that:

* Your inventory file is correctly set up
* Ansible is configured to connect to the target hosts

Running example

```bash
ansible-playbook -i your_inventory_file your_playbook.yaml
```

**Hints:**
If you need to run multiple ansible at one time, write a new yaml file:

```yaml
- import_playbook: <playbook1.yaml>
- import_playbook: <playbook2.yaml>
- import_playbook: <playbook3.yaml>
- import_playbook: <playbook4.yaml>
```

Replace <playbook1.yaml>, <playbook2.yaml>, etc., with the respective names of your playbook files.


Then, follow these steps in order:

*  Gather system information

```bash
ansible-playbook -i your_inventory_file collect_system_info.yaml
```

*  Configure firewall

```bash
ansible-playbook -i your_inventory_file new_configure_firewall.yaml
```

*  Mount disk

```bash
ansible-playbook -i your_inventory_file new_configure_firewall.yaml
```

Note: You can use the system information obtained earlier to modify the mount.yaml file as needed

```bash
vim mount.yaml
```

```yaml
  - name: format the volume as ext4
      community.general.filesystem:
      # /dev/nvme1n1 is the actual hardware device to be operated on
        dev: /dev/nvme1n1
      # ext4 is a commonly used file system type in Linux
        fstype: ext4
      become: true

    - name: mount the filesystem
      ansible.posix.mount:
        name: data
        src: /dev/nvme1n1
        fstype: ext4
        state: mounted
      become: true
```

* Build and configure the virtual environment

  * Setup Python 3.9 virtual environment

  ```bash
  ansible-playbook -i your_inventory_file virtualenv_python39.yaml
  ```

  * Distribute requirements.txt for building virtual environments

  ```bash
    ansible-playbook -i your_inventory_file distribution_requirements.yaml
  ```

  * Configure virtual environment

   ```bash
  ansible-playbook -i your_inventory_file setup_venv.yaml
  ansible-playbook -i your_inventory_file install_hh_suite3.yaml
  ansible-playbook -i your_inventory_file install_s4pred.yaml
  ```

* Deploy the required datasets

```bash
ansible-playbook -i your_inventory_file download_and_extract.yaml
```

* Distribute files related to executing the data pipeline

```bash
ansible-playbook -i your_inventory_file distribute_pipeline_files.yaml
```

* Divide execution tasks

```bash
ansible-playbook -i your_inventory_file split_distribute_generate_fasta.yaml
```

***Note the changes in split_experiment_ids.yaml***

```yaml
- hosts: control
  tasks:

    # Replace <some number> with the desired number of lines per chunk
    - name: Split experiment_ids.txt into chunks of <some number> lines each
      ansible.builtin.shell: split -l <some number> -d --additional-suffix=.txt experiment_ids.txt experiment_ids_
      args:
        chdir: /home/ec2-user/
      register: split_result
```

* After the task ends, run the following code to collect the results

```bash
ansible-playbook -i your_inventory_file get_all_experiment_fasta.yaml
ansible-playbook -i your_inventory_file consolidate_all_fasta_files.yaml
ansible-playbook -i your_inventory_file process_data_get_final_results.yaml
```

### Prometheus and Grafana

* Switch to the directory where Prometheus is configured

```bash
  cd /etc/prometheus/
```

* Move the alert_rules.yaml file into the /etc/prometheus/ director

* Use the vi editor with sudo privileges to modify the prometheus.yml file

```bash
sudo vi prometheus.yml
```

```yaml
# Load rules once and periodically evaluate them according to the glo
bal 'evaluation_interval'.
rule_files:
   - "alert_rules.yaml"
  # - "second_rules.yml"
```

```yaml
# A scrape configuration containing exactly one endpoint to scrape:
# Here it's Prometheus itself.
scrape_configs:
  # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
  - job_name: 'prometheus'

    # Override the global default and scrape targets from this job every 5 seconds.
    scrape_interval: 5s
    scrape_timeout: 5s

    # metrics_path defaults to '/metrics'
    # scheme defaults to 'http'.

    static_configs:
      - targets: ['<your host ip>:9090']

  - job_name: node
    # If prometheus-node-exporter is installed, grab stats about the local
    # machine by default.
    static_configs:
      - targets: ['<your host ip>:9100', '<your client ip>:9100', '<your cluster1 ip>:9100', '<your cluster2 ip>:9100', '<your cluster3 ip>:9100', '<your cluster4 ip>:9100','<your cluster5 ip>:9100']
```

* Creating a new file named node_exporter.service to set up Node Exporter 

```bash
touch node_exporter.service
```

```bash
vi node_exporter.service
```

```plaintext
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=root
Group=root
Type=simple
ExecStart=/usr/bin/node_exporter

[Install]
WantedBy=multi-user.target
```

* Use node_exporter_playbook.yaml to deploy Node Exporter

```bash
ansible-playbook -i your_inventory_file node_exporter_playbook.yaml
```

* Starting Prometheus
```bash
sudo prometheus --config.file=/etc/prometheus/prometheus.yml
```

* Reloading Systemd Daemon
```bash
sudo systemctl daemon-reload
```

* Starting and Enabling Grafana Service
```bash
sudo systemctl enable grafana-server.service
sudo systemctl start grafana-server
```
