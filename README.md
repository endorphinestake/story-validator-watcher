
![watcher screen](https://github.com/endorphinestake/story-validator-watcher/blob/main/images/story-validator-watcher.png)

<font size = 7><center><b><u>About Story Validator Watcher</u></b></center></font>
-  Cosmos Validator Watcher is set to streamline monitoring and interaction with Cosmos-based blockchains and validators by [Kiln](https://github.com/kilnfi/cosmos-validator-watcher).
-  This custom tool does not allow you to receive data from the blockchain in real time and distribute it to the watcher.
-  Therefore, our team wrote [pars_script](https://github.com/endorphinestake/story-validator-watcher/tree/main/pars_script) which adds active validators to the watcher configuration in real time.

[![Grafana Dashboard Demo by ](https://img.shields.io/badge/Grafana%20Dashboard-Demo%20Online-blue?style=for-the-badge&logo=grafana&logoColor=white)](https://story-watcher.endorphinestake.com/d/d79d55e7-6e70-4725-b78c-b22db4a71b08/modified-story-validator-watcher?orgId=1&refresh=5s&theme=light)


### If you want to set up your own Story Validator Watcher - let's continue!

Import the GPG key for Grafana:
```bash
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
```

Add the Grafana repository to the APT sources:
```bash 
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
```

Update the package lists:
```bash
sudo apt update
```

Install the grafana:
```bash
sudo apt install grafana
```

Start and enable service:
```bash
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

Check status grafana-server:
```bash
sudo systemctl status grafana-server
```
- If everything works fine, enter your `Public IP:3000` in searchbar. You will see the login page: `admin` as default username and password.



Install go:
```bash
sudo apt-get install -y snapd
sudo snap install go --classic
sudo 
```
Build cosmos-validator-watcher:
```bash
git clone https://github.com/kilnfi/cosmos-validator-watcher
cd cosmos-validator-watcher
git checkout v0.14.0
make build
cd build
mv cosmos-validator-watcher /usr/local/bin/
```



```bash
git clone https://github.com/LinGena/rbc
```
```bash
apt install python3-pip
```

```bash
pip install vk_api
pip install schedule
```

```bash
cd rbc
python3 main.py
```


Download Prometheus:
```bash
sudo wget https://github.com/prometheus/prometheus/releases/download/v2.47.0/prometheus-2.47.0.linux-amd64.tar.gz
```

Extract Files:
```bash
sudo tar vxf prometheus*.tar.gz
```

Create a user for prometeus:
```bash
sudo groupadd --system prometheus
sudo useradd -s /sbin/nologin --system -g prometheus prometheus
```

Create directories for prometheus:
```bash
sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus
cd prometheus*/
```

Move the binary files:
```bash
sudo mv prometheus /usr/local/bin
sudo mv promtool /usr/local/bin
sudo mv console* /etc/prometheus
sudo mv prometheus.yml /etc/prometheus
```

Set owner:
```bash
sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool
sudo chown prometheus:prometheus /etc/prometheus
sudo chown -R prometheus:prometheus /etc/prometheus/consoles
sudo chown -R prometheus:prometheus /etc/prometheus/console_libraries
sudo chown -R prometheus:prometheus /var/lib/prometheus
```

Change config:
```bash
sudo nano /etc/prometheus/prometheus.yml
```

```bash
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'watcher'
    static_configs:
      - targets: ['localhost:8080']  # Adjust the target to your node exporter endpoint

  - job_name: 'story node'
    static_configs:
      - targets: ['135.181.208.245:26660']  # Adjust the target to your story node exporter endpoint
```

Create prometeus service:
```bash
sudo nano /etc/systemd/system/prometheus.service
```

```bash
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
 --config.file /etc/prometheus/prometheus.yml \
 --storage.tsdb.path /var/lib/prometheus/ \
 --web.console.templates=/etc/prometheus/consoles \
 --web.console.libraries=/etc/prometheus/console_libraries

[Install]
WantedBy=multi-user.target
```

Start and enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable prometheus
sudo systemctl start prometheus
```

- If everything works fine, enter your `Public IP:3000` in searchbar. You will see the login page: `admin` as default username and password.

- Click `Dashboard` - `New` - `Import`.

![grafana-watcher-1](https://github.com/endorphinestake/story-validator-watcher/blob/main/images/grafana-watcher-1.png)

- Download [json](https://github.com/endorphinestake/story-validator-watcher/blob/d2d5956e5e0102274dbfbf308bc47be66dcc40d9/Modified%20Story%20Validator%20Watcher-1733176062943.json) for Story Validator Watcher.
- Click `Upload dashboard JSON file` and drop here your file.

![grafana-watcher-2](https://github.com/endorphinestake/story-validator-watcher/blob/main/images/grafana-watcher-2.png)

- Be sure to specify the data source - `prometheus-1` and click `Import`.

![grafana-watcher-3](https://github.com/endorphinestake/story-validator-watcher/blob/main/images/grafana-watcher-3.png)

- Completed, if everything is done correctly, your dashboard will start displaying data.

![grafana-watcher-4](https://github.com/endorphinestake/story-validator-watcher/blob/main/images/grafana-watcher-4.png)


## Features pars_script
