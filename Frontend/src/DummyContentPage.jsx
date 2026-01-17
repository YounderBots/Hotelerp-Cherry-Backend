import React, { useState } from 'react'
import Tabs, { Tab } from './stories/Tabs'
import TableTemplate from './stories/TableTemplate'
import Accordion from './stories/Accordion'
// import Select from './stories/Form/Select'


import Form from './stories/Form/Form';
import Input from './stories/Form/Input';
import Textarea from './stories/Form/Textarea';
import Select from './stories/Form/Select';
import Checkbox,{CheckboxGroup} from './stories/Form/Checkbox';
import RadioGroup from './stories/Form/Radio';
import Switch from './stories/Form/Switch';


const tableColumnsContent = [
  {
    key: 'user',
    title: 'User',
    type: 'avatar',
    width: '250px'
  },
  {
    align: 'center',
    key: 'role',
    title: 'Role'
  },
  {
    align: 'center',
    key: 'status',
    title: 'Status',
    type: 'badge'
  },
  {
    align: 'center',
    key: 'lastLogin',
    title: 'Last Login'
  }
]

const UserInfoInitial = [
        {
          avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=32&h=32&fit=crop&crop=face',
          email: 'john@example.com',
          id: 1,
          lastLogin: '2024-01-15',
          name: 'John Doe',
          role: 'Admin',
          status: 'active',
          user: {
            email: 'john@example.com',
            name: 'John Doe',
            src: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=32&h=32&fit=crop&crop=face'
          }
        },
        {
          avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=32&h=32&fit=crop&crop=face',
          email: 'jane@example.com',
          id: 2,
          lastLogin: '2024-01-10',
          name: 'Jane Smith',
          role: 'User',
          status: 'pending',
          user: {
            email: 'jane@example.com',
            name: 'Jane Smith',
            src: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=32&h=32&fit=crop&crop=face'
          }
        },
        {
          avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=32&h=32&fit=crop&crop=face',
          email: 'mike@example.com',
          id: 3,
          lastLogin: '2024-01-05',
          name: 'Mike Johnson',
          role: 'Moderator',
          status: 'inactive',
          user: {
            email: 'mike@example.com',
            name: 'Mike Johnson',
            src: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=32&h=32&fit=crop&crop=face'
          }
        },
        {
          avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=32&h=32&fit=crop&crop=face',
          email: 'sarah@example.com',
          id: 4,
          lastLogin: '2024-01-14',
          name: 'Sarah Wilson',
          role: 'User',
          status: 'active',
          user: {
            email: 'sarah@example.com',
            name: 'Sarah Wilson',
            src: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=32&h=32&fit=crop&crop=face'
          }
        },
        {
          avatar: 'https://images.unsplash.com/photo-1507591064344-4c6ce005b128?w=32&h=32&fit=crop&crop=face',
          email: 'alex@example.com',
          id: 5,
          lastLogin: '2024-01-12',
          name: 'Alex Chen',
          role: 'Developer',
          status: 'active',
          user: {
            email: 'alex@example.com',
            name: 'Alex Chen',
            src: 'https://images.unsplash.com/photo-1507591064344-4c6ce005b128?w=32&h=32&fit=crop&crop=face'
          }
        }
      ]



const TableTemplateComponent = () => {
  const [tableColumns, setTableColumns] = useState(tableColumnsContent);
  const [tableData,setTableData]=useState(UserInfoInitial)
  return (
    <TableTemplate
      columns={tableColumns}
      data={tableData}
      pageSize={3}
      pagination
      title="Team Members"
      variant="striped"
    />
  )
}


const MultiSelectDemo = () => {
  const [selected, setSelected] = useState([]);
  const options = [{
    value: 'react',
    label: 'React'
  }, {
    value: 'vue',
    label: 'Vue'
  }, {
    value: 'angular',
    label: 'Angular'
  }, {
    value: 'svelte',
    label: 'Svelte'
  }];
  return <div style={{
    maxWidth: '400px',
    padding: '2rem'
  }}>
    <Select label="Select frameworks" options={options} value={selected} multiple onChange={e => {
      setSelected(e.target.value); // ✅ ARRAY
    }} helperText="Select one or more frameworks" />
  </div>;
}


const FormContent =() => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    country: '',
    bio: '',
    notifications: [],
    subscription: 'free',
    terms: false,
    newsletter: true
  });
  const countries = [{
    value: '',
    label: 'Select a country',
    disabled: true
  }, {
    value: 'us',
    label: 'United States'
  }, {
    value: 'ca',
    label: 'Canada'
  }, {
    value: 'uk',
    label: 'United Kingdom'
  }, {
    value: 'au',
    label: 'Australia'
  }];
  const notificationOptions = [{
    value: 'email',
    label: 'Email'
  }, {
    value: 'sms',
    label: 'SMS'
  }, {
    value: 'push',
    label: 'Push'
  }];
  const subscriptionOptions = [{
    value: 'free',
    label: 'Free'
  }, {
    value: 'pro',
    label: 'Pro ($9.99/month)'
  }, {
    value: 'enterprise',
    label: 'Enterprise ($49.99/month)'
  }];
  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };
  const handleSubmit = async e => {
    e.preventDefault();
    console.log('Form submitted:', formData);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    alert('Form submitted successfully!');
  };
  return <div>
      <Form title="Create Account" subtitle="Join our community today" onSubmit={handleSubmit} submitLabel="Sign Up">
        <div className="form-row">
          <Input label="First Name" required value={formData.firstName} onChange={e => handleChange('firstName', e.target.value)} placeholder="John" />
          <Input label="Last Name" required value={formData.lastName} onChange={e => handleChange('lastName', e.target.value)} placeholder="Doe" />
        </div>
        <div className="form-row">

        <Input label="Email Address" type="email" required value={formData.email} onChange={e => handleChange('email', e.target.value)} placeholder="john@example.com" helperText="We'll never share your email" />

        <Input label="Password" type="password" required value={formData.password} onChange={e => handleChange('password', e.target.value)} helperText="At least 8 characters with letters and numbers" />

        </div>

        <Select label="Country" required options={countries} value={formData.country} onChange={e => handleChange('country', e.target.value)} />

        <Textarea label="About You" value={formData.bio} onChange={e => handleChange('bio', e.target.value)} placeholder="Tell us about yourself..." maxLength={500} rows={3} />

        <CheckboxGroup label="Notification Preferences" options={notificationOptions} value={formData.notifications} onChange={value => handleChange('notifications', value)} helperText="Choose how you want to be notified" />

        <RadioGroup label="Subscription Plan" required options={subscriptionOptions} value={formData.subscription} onChange={value => handleChange('subscription', value)} layout="vertical" />

        <div className="form-row">
          <Checkbox label="I agree to the Terms of Service" required checked={formData.terms} onChange={e => handleChange('terms', e.target.checked)} />
          
          <Switch label="Subscribe to newsletter" checked={formData.newsletter} onChange={e => handleChange('newsletter', e.target.checked)} />
        </div>
      </Form>
    </div>;
}
export const AccordionComponent = () => {
  return (<Accordion
    bordered
    defaultOpen={[
      0
    ]}
    items={[
      {
        content: <MultiSelectDemo />,
        title: 'What is your return policy?'
      },
      {
        content: <FormContent />,
        title: 'How long does shipping take?'
      },
      {
        content: 'Yes, to 50+ countries...',
        title: 'Do you ship internationally?'
      },
      {
        content: 'A tracking number will be emailed...',
        title: 'How can I track my order?'
      }
    ]}
    size="lg"
    variant="classic"
  />)
}


const DummyContentPage = () => {
  return (
    <div>
      <Tabs variant="default">
        <Tab label="Profile">
          <TableTemplateComponent />
        </Tab>
        <Tab label="Accordion">
          <AccordionComponent />
        </Tab>
      </Tabs>
    </div>
  )
}

export default DummyContentPage