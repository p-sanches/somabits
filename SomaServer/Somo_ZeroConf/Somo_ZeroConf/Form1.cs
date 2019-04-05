using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using Mono.Zeroconf;

namespace Somo_ZeroConf
{
    public partial class Form1 : Form
    {
        public DataSet devices = new DataSet();  //Contains tables for each device with components info
        public DataSet devices_selected = new DataSet();  //Contains tables for selected device with components info
        public DataTable device_info = new DataTable(); // Contains basic info of all the available devices
        public DataTable device_info_selected = new DataTable(); // Contains basic info of selected devices



        public Form1()
        {
            device_info.Columns.Add("Name", typeof(string));
            device_info.Columns.Add("IP", typeof(System.Net.IPAddress));
            device_info.Columns.Add("Port", typeof(System.Int16));
            device_info.Columns.Add("Attached Sensors/Actuators", typeof(System.Int16));

            device_info_selected.Columns.Add("Name", typeof(string));
            device_info_selected.Columns.Add("IP", typeof(System.Net.IPAddress));
            device_info_selected.Columns.Add("Port", typeof(System.Int16));
            device_info_selected.Columns.Add("Attached Sensors/Actuators", typeof(System.Int16));
            InitializeComponent();
            
        }

        private void button1_Click(object sender, EventArgs e)
        {
            ServiceBrowser browser = new ServiceBrowser();

            //
            // Configure the code that will be called back when the information
            // becomes available
            //
            browser.ServiceAdded += delegate (object o, ServiceBrowseEventArgs argss) {
                
                argss.Service.Resolved += delegate (object oo, ServiceResolvedEventArgs argsss) {
                    IResolvableService s = (IResolvableService)argsss.Service;
                    
                    DataRow new_device = device_info.NewRow();
                    new_device["Name"] = s.Name;
                    new_device["IP"] = s.HostEntry.AddressList[0];
                    new_device["Port"] = s.Port;
                    new_device["Attached Sensors/Actuators"] = s.TxtRecord.Count;


                    bool contains = device_info.AsEnumerable().Any(row => s.Name == row.Field<String>("Name"));
                    if (!contains)
                    {
                        device_info.Rows.Add(new_device);
                        DataTable device_components = new DataTable(s.Name);
                        device_components.Columns.Add("Type", typeof(string));
                        device_components.Columns.Add("OSC Address", typeof(string));
                        device_components.Columns.Add("Range", typeof(string));

                        for (int i=0; i< s.TxtRecord.Count;i++)
                        {
                            
                            DataRow new_device_component = device_components.NewRow();
                            TxtRecordItem Component= s.TxtRecord.BaseRecord.GetItemAt(i);
                            
                            new_device_component["Type"] = Component.Key;

                            String[] ComponentList = Component.ValueString.Split(':');
                            new_device_component["OSC Address"] = ComponentList[0];
                            new_device_component["Range"] = ComponentList[1];
                            device_components.Rows.Add(new_device_component);
                        }

                        devices.Tables.Add(device_components);
                        
                    }

                    
                  
                };
                argss.Service.Resolve();
            };

            
            browser.Browse("_http._udp.", "local"); // Triggering the discovery request
            dataGridView1.DataSource = device_info; // Binding DataGridView with main table

            dataGridView1.Columns[0].Width = 220;
            dataGridView1.Columns[1].Width = 140;
            dataGridView1.Columns[2].Width = 100;
            dataGridView1.Columns[3].Width = 250;

            //
            // Adding Checkbox column in table
            //

            DataGridViewCheckBoxColumn chk = new DataGridViewCheckBoxColumn(); 
            chk.HeaderText = "Select";
            chk.Name = "Checkbox";
            chk.Width = dataGridView1.Width- dataGridView1.Columns[0].Width- dataGridView1.Columns[1].Width- dataGridView1.Columns[2].Width- dataGridView1.Columns[3].Width-45;
            dataGridView1.Columns.Add(chk);
            
           
        }

        private void timer1_Tick(object sender, EventArgs e)
        {

            dataGridView1.Refresh();
            
        }

        private void dataGridView1_CellClick(object sender, DataGridViewCellEventArgs e)
        {
            if(e.ColumnIndex==0)
            {
                Form2 secondForm = new Form2();
                secondForm.dataGridView2.DataSource = devices.Tables[device_info.Rows[e.RowIndex].Field<string>("Name")];
                secondForm.dataGridView2.Columns[0].Width = 120;
                secondForm.dataGridView2.Columns[1].Width = 180;
                secondForm.dataGridView2.Columns[2].Width = 124;
                
                secondForm.ShowDialog();
                
            }
        }

        private void button2_Click(object sender, EventArgs e)
        {
            for(int i=0;i< device_info.Rows.Count;i++)
            {
                DataGridViewCheckBoxCell checkCell =(DataGridViewCheckBoxCell)dataGridView1.Rows[i].Cells["Select"];
                if ((bool)checkCell.Value == true)
                {
                    device_info_selected.Rows.Add(device_info.Rows[i]); // Now we have info for selected devices
                    devices_selected.Tables.Add(devices.Tables[device_info.Rows[i].Field<string>("Name")]); // and their components
                }
            }

            //OSC part for Martina
        }
    }
}
