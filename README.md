A. Feinberg Nov 2022

Python scripts to load available Hg observation network data into a dataframe and output as a csv file. For most networks, these are outputted as daily means. Several EMEP sites have coarser time resolution for some of the measurement stations, so several options of time resolutions for outputted mean data are provided. This includes:

-CAPMoN (Canada): CAPMoN_network.py
Data can be accessed at: https://donnees.ec.gc.ca/data/air/monitor/monitoring-of-atmospheric-gases/total-gaseous-mercury-tgm/?lang=en

-AMNet (USA): AMNet_network.py
Data can be accessed at: https://nadp.slh.wisc.edu/networks/atmospheric-mercury-network/

-EMEP (Europe/Antarctica): EMEP_network.py
Data can be accessed at: https://ebas.nilu.no/data-access/

-GMOS (Global): GMOS_network.py
Data can be accessed at (currently under maintenance): https://sdi.iia.cnr.it/gos4mcat/srv/eng/catalog.search

-MOEJ (Japan): MOEJ_network.py
Data can be requested from the Ministry of the Environment Japan (MOEJ). For publication, see:  https://doi.org/10.3390/atmos10070362

-FMI (Finland) network: Finland_network.py
These data are submitted to EMEP, but an updated version was provided by K. Kyllönen.

-MHD data: MHD.py
These updated data for Mace Head were provided by D. Custodio 

-ELA data: ELA.py
These data for Experimental Lakes Area were provided by V. St. Louis

-MLO data: MLO_data.py
These data for Mauna Loa from the EPA measurements 2002–2010 were provided by M. Landis
