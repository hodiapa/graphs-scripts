import sys, os, re
import logging
import numpy as np
from collections import defaultdict
import cluster_simulation_protos_pb2
import matplotlib.pyplot as plt

def usage():
    print "Usage: Input 1 Dir of protobuf Input 2 string of rows to perform"
    sys.exit(1)

logging.debug("len(sys.argv): " + str(len(sys.argv)))

if len(sys.argv) < 2:
    logging.error("Not enough arguments provided.")
    usage()

try:
    input_dir = sys.argv[1]
    rows_string = sys.argv[2]

except:
    usage()
policies = rows_string.split(",")
policies_dict_name_legend = {}
policies_single_savings = {}
policies_multi_savings = {}
policies_single_batch_think = {}
policies_multi_batch_think = {}
policies_single_service_think = {}
policies_multi_service_think = {}
policies_single_kw = {}
policies_multi_kw = {}
policies_single_idle = {}
policies_multi_idle = {}
policies_single_service_90p_first = {}
policies_multi_service_90p_first = {}
policies_single_service_90p_fully = {}
policies_multi_service_90p_fully = {}

for policy_entry in policies:
    name = policy_entry.split(';')[0]
    legend = policy_entry.split(';')[1]
    policies_dict_name_legend[name] = legend
input_protobuff_monolithic_single = ""
input_protobuff_monolithic_multi = ""
for fn in os.listdir(input_dir):
     if os.path.splitext(fn)[1] == ".protobuf":
        if fn.startswith("google-monolithic-multi_path"):
            input_protobuff_monolithic_multi = os.path.join(input_dir,fn)
        elif fn.startswith("google-monolithic-single_path"):
            input_protobuff_monolithic_single = os.path.join(input_dir,fn)


if input_protobuff_monolithic_multi == "" or input_protobuff_monolithic_multi == "" :
    print "Single or Multi Path protobuf not found"
    sys.exit(1)


experiment_result_set_single = cluster_simulation_protos_pb2.ExperimentResultSet()
experiment_result_set_multi = cluster_simulation_protos_pb2.ExperimentResultSet()
print("Empieza a leer single")
single_infile = open(input_protobuff_monolithic_single, "rb")
experiment_result_set_single.ParseFromString(single_infile.read())
single_infile.close()
print("Termina de leer single")

for env in experiment_result_set_single.experiment_env:
    for exp_result in env.experiment_result:
        eff = exp_result.efficiency_stats
        for policy_name in policies_dict_name_legend.keys():
        #if any(policy_name in eff.power_off_policy.name for policy_name in policies_dict_name_legend.keys()):
            if policy_name in eff.power_off_policy.name:
                policies_single_savings[policy_name] = (1 - (eff.total_energy_consumed / eff.current_energy_consumed)) * 100
                #kwh
                policies_single_kw[policy_name] = eff.kwh_saved_per_shutting
                #idle
                policies_single_idle[policy_name] = (eff.avg_number_machines_on / 10000 - max(
                    exp_result.cell_state_avg_cpu_utilization, exp_result.cell_state_avg_mem_utilization)) * 100
                for workload_stat in exp_result.workload_stats:
                    if workload_stat.workload_name == "Service":
                        # queue times
                        policies_single_service_90p_first[policy_name] = workload_stat.job_queue_time_till_first_scheduled_90_percentile
                        policies_single_service_90p_fully[policy_name] = workload_stat.job_queue_time_till_fully_scheduled_90_percentile
                        #job think time
                        policies_single_service_think[policy_name] = workload_stat.job_think_times_90_percentile
                    elif workload_stat.workload_name == "Batch":
                            policies_single_batch_think[policy_name] = workload_stat.job_think_times_90_percentile

print("Empieza a leer multi")
multi_infile = open(input_protobuff_monolithic_multi, "rb")
experiment_result_set_multi.ParseFromString(multi_infile.read())
multi_infile.close()
print("Termina de leer multi")

for env in experiment_result_set_multi.experiment_env:
    for exp_result in env.experiment_result:
        eff = exp_result.efficiency_stats
        for policy_name in policies_dict_name_legend.keys():
        #if any(policy_name in eff.power_off_policy.name for policy_name in policies_dict_name_legend.keys()):
            if policy_name in eff.power_off_policy.name:
                policies_multi_savings[policy_name] = (1 - (eff.total_energy_consumed / eff.current_energy_consumed)) * 100
                #kwh
                policies_multi_kw[policy_name] = eff.kwh_saved_per_shutting
                #idle
                policies_multi_idle[policy_name] = (eff.avg_number_machines_on/10000 - max(exp_result.cell_state_avg_cpu_utilization, exp_result.cell_state_avg_mem_utilization))*100
                #queuetimes
                for workload_stat in exp_result.workload_stats:
                    if workload_stat.workload_name == "Service":
                        policies_multi_service_90p_first[policy_name] = workload_stat.job_queue_time_till_first_scheduled_90_percentile
                        policies_multi_service_90p_fully[policy_name] = workload_stat.job_queue_time_till_fully_scheduled_90_percentile
                        #job think time
                        policies_multi_service_think[policy_name] = workload_stat.job_think_times_90_percentile
                    elif workload_stat.workload_name == "Batch":
                        policies_multi_batch_think[policy_name] = workload_stat.job_think_times_90_percentile

#kwh

N = len(policies_dict_name_legend.keys())
figure = plt.figure(figsize=(9, 7.5))
plt.rcParams.update({'font.size': 25})
ind = np.arange(N)  # the x locations for the groups
width = 0.35
#ax1 = figure.add_subplot(1, 1, 1, position = [0.1, 0.2, 0.75, 0.75])
figure, ax1 = plt.subplots()
savingsSingleBar = ax1.bar(ind, policies_single_savings.values(), width, color='#007dad', zorder=1)
savingsMultiBar = ax1.bar(ind+width, policies_multi_savings.values(), width, color='#ec6200', zorder=1)

ax1.set_ylabel('Total Savings %')
ax1.set_ylim([10, 25])
ax1.set_xlabel('Energy Policy')
ax1.set_xticks(ind + width)
policies_dict_name_legend.values()
ax1.set_xticklabels(policies_dict_name_legend.values())

ax2 = ax1.twinx()
ax2.plot(ind+width,policies_single_kw.values(), linestyle='--', color='#18b0ea', linewidth=3, zorder=2)
ax2.plot(ind+width,policies_multi_kw.values(),linestyle='--', color='#ffa038', linewidth=3, zorder=2)
ax2.set_ylabel('KWh saved / shutting')

plt.rc('legend',**{'fontsize':16})
ax1.legend((savingsSingleBar[0], savingsMultiBar[0]), ("Single", "Multi"))
plt.tight_layout()
#plt.show()
figure.savefig(os.path.join(input_dir,'monoliticsavingsvskwhpershutting.pdf'), format='PDF')

#idle

N = len(policies_dict_name_legend.keys())
figure = plt.figure(figsize=(9, 7.5))
plt.rcParams.update({'font.size': 25})
ind = np.arange(N)  # the x locations for the groups
width = 0.35
#ax1 = figure.add_subplot(1, 1, 1, position = [0.1, 0.2, 0.75, 0.75])
figure, ax1 = plt.subplots()
savingsSingleBar = ax1.bar(ind, policies_single_savings.values(), width, color='#007dad')
savingsMultiBar = ax1.bar(ind+width, policies_multi_savings.values(), width, color='#ec6200')

ax1.set_ylabel('Total Savings %')
ax1.set_ylim([10, 25])
ax1.set_xlabel('Energy Policy')
ax1.set_xticks(ind + width)
policies_dict_name_legend.values()
ax1.set_xticklabels(policies_dict_name_legend.values())

ax2 = ax1.twinx()
ax2.plot(ind+width,policies_single_idle.values(), linestyle='--', color='#18b0ea', linewidth=3)
ax2.plot(ind+width,policies_multi_idle.values(),linestyle='--', color='#ffa038', linewidth=3)
ax2.set_ylabel('Idle Resources %')

plt.rc('legend',**{'fontsize':16})
ax1.legend((savingsSingleBar[0], savingsMultiBar[0]), ("Single", "Multi"))
plt.tight_layout()
#plt.show()
figure.savefig(os.path.join(input_dir,'monoliticsavingsvsidle.pdf'), format='PDF')

#queuetimes

N = len(policies_dict_name_legend.keys())
figure = plt.figure(figsize=(9, 7.5))
plt.rcParams.update({'font.size': 25})
ind = np.arange(N)  # the x locations for the groups
width = 0.35
#ax1 = figure.add_subplot(1, 1, 1, position = [0.1, 0.2, 0.75, 0.75])
figure, ax1 = plt.subplots()
savingsSingleBar = ax1.bar(ind, policies_single_savings.values(), width, color='#007dad')
savingsMultiBar = ax1.bar(ind+width, policies_multi_savings.values(), width, color='#ec6200')

ax1.set_ylabel('Total Savings %')
ax1.set_ylim([10, 25])
ax1.set_xlabel('Energy Policy')
ax1.set_xticks(ind + width)
policies_dict_name_legend.values()
ax1.set_xticklabels(policies_dict_name_legend.values())

ax2 = ax1.twinx()
firstPlot = ax2.plot(ind+width, policies_single_service_90p_first.values(),  marker='.', markersize=10, linestyle='-', color='#18b0ea', linewidth=3)
fullyPlot = ax2.plot(ind+width, policies_single_service_90p_fully.values(), marker='^', markersize=10, linestyle='--', color='#04d8ff', linewidth=3)

ax2.plot(ind+width,policies_multi_service_90p_first.values(),linestyle='-', marker='.', markersize=10, color='#ffa038', linewidth=3)
ax2.plot(ind+width,policies_multi_service_90p_fully.values(),linestyle='--', marker='', markersize=10, color='#ff9626', linewidth=3)
ax2.set_ylabel('Job queue times (s)')

plt.rc('legend',**{'fontsize':16})
ax1.legend((firstPlot[0], fullyPlot[0]), ("First sch.", "Fully sch."))
plt.tight_layout()
#plt.show()
figure.savefig(os.path.join(input_dir,'monoliticsavingsvqueue.pdf'), format='PDF')

#job think

N = len(policies_dict_name_legend.keys())
figure = plt.figure(figsize=(9, 7.5))
plt.rcParams.update({'font.size': 25})
ind = np.arange(N)  # the x locations for the groups
width = 0.35
#ax1 = figure.add_subplot(1, 1, 1, position = [0.1, 0.2, 0.75, 0.75])
figure, ax1 = plt.subplots()
savingsSingleBar = ax1.bar(ind, policies_single_savings.values(), width, color='#007dad')
savingsMultiBar = ax1.bar(ind+width, policies_multi_savings.values(), width, color='#ec6200')

ax1.set_ylabel('Total Savings %')
ax1.set_ylim([10, 25])
ax1.set_xlabel('Energy Policy')
ax1.set_xticks(ind + width)
policies_dict_name_legend.values()
ax1.set_xticklabels(policies_dict_name_legend.values())

ax2 = ax1.twinx()
batchPlot = ax2.plot(ind+width, policies_single_batch_think.values(), marker='^', markersize=10, linestyle='--', color='#04d8ff', linewidth=3)
servicePlot = ax2.plot(ind+width, policies_single_service_think.values(),  marker='.', markersize=10, linestyle='-', color='#18b0ea', linewidth=3)

ax2.plot(ind+width,policies_multi_batch_think.values(),linestyle='--', marker='^', markersize=10, color='#ff9626', linewidth=3)
ax2.plot(ind+width,policies_multi_service_think.values(),linestyle='-', marker='.', markersize=10, color='#ffa038', linewidth=3)
ax2.set_ylabel('Job think time (s)')

plt.rc('legend',**{'fontsize':16})
ax1.legend((batchPlot[0], servicePlot[0]), ("Batch", "Service"))
plt.tight_layout()
#plt.show()
figure.savefig(os.path.join(input_dir,'monoliticsavingsvjobthink.pdf'), format='PDF')