# On the Interaction of Feature Toggles

This is the companion repository of our submission "On the Interaction of Feature Toggles", submitted to VaMoS 2022.

### Organisation

Measurements and details about the performances can be consulted in the **data** folder.

Source code can be found in the **src** directory.

The **results** folder contains the results shown in the submission, as well as complementary results.

## In a nutshell

We analyse the feature toggles of 5 real-world projects written in go.

We propose an approach to automatically extract the depedencies out a config file, like this one :

![config](results/kops_config_screenshot.png)

We download the project, statically analyse the code to mine the dependencies between toggles, and extract a feature toggle model, like this one

![ftm](results/FTM_01.png)
