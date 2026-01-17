import React, { useState } from 'react'
import './Playground.css'
import sampleImage from './assets/sample.jpg'


const ProfileCard = ({ info, actions }) => {
  const [open, setOpen] = useState(false);

  return (
    <div className="profile-card">
      <div className="card-header">
        <button
          className="card-menu"
          onClick={() => setOpen(prev => !prev)}
        >
          ⋮
        </button>

        {open && (
          <div className="card-dropdown">
            {actions.map(action => (
              <button
                key={action.label}
                onClick={() => {
                  action.onClick(info.id);
                  setOpen(false);
                }}
              >
                {action.label}
              </button>
            ))}
          </div>
        )}
      </div>

      <img
        src={info.ProfilePic}
        alt={info.name}
        className="profile-image"
      />

      <h3 className="profile-name">{info.name}</h3>
      <p className="profile-role">{info.role}</p>
    </div>
  );
};



const Playground = () => {
  const intialData = [
    {
      'name': 'John Doe',
      'role': 'Web Designer',
      'ProfilePic': "https://randomuser.me/api/portraits/men/32.jpg",
      'id': '1',
    },
    {
      'name': 'John Doe',
      'role': 'Web Designer',
      'ProfilePic': "https://randomuser.me/api/portraits/men/32.jpg",
      'id': '2',
    },
    {
      'name': 'John Doe',
      'role': 'Web Designer',
      'id': '3',
      'ProfilePic': "https://randomuser.me/api/portraits/men/32.jpg"
    },
    {
      'id': '4',
      'name': 'John Doe',
      'role': 'Web Designer',
      'ProfilePic': "https://randomuser.me/api/portraits/men/32.jpg"
    },
  ]

  const [allInfo, setAllInfo] = useState(intialData)

  const editNameFunc = (id) => {
    const selectedElement = allInfo.find(item => item.id == id);
    if (!selectedElement) return alert('No Such elements');

    const newName = 'Ganesh';
    setAllInfo(prev => prev.map(
      item => item.id == id ? { ...item, name: 'Ganesh' } : item

    ))
  }




  const data = {
    'allData': allInfo,
    'actions': [
      {
        'label': 'Edit Name',
        'onClick': editNameFunc 
      },
      {
        'label': 'Edit Role',
        'onClick': ''
      }
    ]

  }








  return (
    <div className='card__grid'>
      {
        data.allData.map(card => <ProfileCard info={card} actions={data.actions} />)
      }

    </div>
  )
}

export default Playground