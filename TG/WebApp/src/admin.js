const userPermissions = ['add_admin', 'delete_admin', 'new_entry', 'modify_entry', 'delete_entry'];

const actions = [
    { perm: 'add_admin', label: 'Add Admin', api: '/admin/add_admin' },
    { perm: 'delete_admin', label: 'Delete Admin', api: '/admin/delete_admin' },
    { perm: 'new_entry', label: 'New Entry', api: '/admin/new_entry' },
    { perm: 'modify_entry', label: 'Modify Entry', api: '/admin/modify_entry' },
    { perm: 'delete_entry', label: 'Delete Entry', api: '/admin/delete_entry' },
];

// Central form field definitions for all actions
const forms = {
    add_admin: [
        { label: 'Username', name: 'username', type: 'text', required: true },
        { label: 'command_list', name: 'email', type: 'email', required: false }
    ],
    delete_admin: [
        { label: 'Username', name: 'username', type: 'text', required: true }
    ],
    modify_entry: [
        { label: 'Entry ID', name: 'entryid', type: 'text', required: true },
        { label: 'New Content', name: 'newcontent', type: 'text', required: true }
    ],
    delete_entry: [
        { label: 'Entry ID', name: 'entryid', type: 'text', required: true }
    ]
};

const tables = [
    {
        name: 'Products',
        fields: [
            { label: 'Image', name: 'image', type: 'file', required: true },
            { label: 'Name', name: 'name', type: 'text', required: true },
            { label: 'Details', name: 'details', type: 'text', required: true },
            { label: 'Speed', name: 'speed', type: 'number', required: false },
            { label: 'Capacity', name: 'capacity', type: 'number', required: false },
            { label: 'Min Temp', name: 'min_temp', type: 'number', required: false },
            { label: 'Max Temp', name: 'max_temp', type: 'number', required: false },
            { label: 'Type', name: 'type', type: 'text', required: false },
            { label: 'Price', name: 'price', type: 'number', required: true }
        ]
    },
    {
        name: 'Users',
        fields: [
            { label: 'User ID', name: 'user_id', type: 'text', required: true },
            { label: 'Username', name: 'username', type: 'text', required: true }
        ]
    },
    {
        name: 'Other',
        fields: [
            { label: 'Field 1', name: 'field1', type: 'text', required: true },
            { label: 'Field 2', name: 'field2', type: 'text', required: false }
        ]
    }
];

const adminButtons = document.getElementById('admin-buttons');
const formContainer = document.getElementById('form-container');

// Render buttons based on permissions
actions.forEach(action => {
    if (userPermissions.includes(action.perm)) {
        const btn = document.createElement('button');
        btn.textContent = action.label;
        btn.onclick = () => showForm(action);
        adminButtons.appendChild(btn);
    }
});

// Render fields for a given form (used for all except new_entry)
function renderFields(form, fields) {
    const container = document.createElement('div');
    fields.forEach(field => {
        if (field.type === 'file') {
            container.innerHTML += `<label><span>${field.label}:</span> <input type="file" name="${field.name}" ${field.required ? 'required' : ''}></label>`;
        } else {
            container.innerHTML += `<label><span>${field.label}:</span> <input type="${field.type}" name="${field.name}" ${field.required ? 'required' : ''}></label>`;
        }
    });
    form.appendChild(container);
}

// Render fields for a table (used for new_entry)
function renderTableFields(form, table) {
    const container = form.querySelector('#dynamic-fields');
    container.innerHTML = '';
    table.fields.forEach(field => {
        if (field.type === 'file') {
            container.innerHTML += `<label><span>${field.label}:</span> <input type="file" name="${field.name}" accept=".png,.jpeg,.jpg" ${field.required ? 'required' : ''}></label>`;
        } else {
            container.innerHTML += `<label><span>${field.label}:</span> <input type="${field.type}" name="${field.name}" ${field.required ? 'required' : ''}></label>`;
        }
    });
}

function showForm(action) {
    formContainer.innerHTML = '';
    const form = document.createElement('form');
    form.innerHTML = `<h3>${action.label}</h3>`;

    if (action.perm === 'new_entry') {
        // Add table selector and dynamic fields container
        form.innerHTML += `<label><span>Table:</span>
            <select name="table" id="table-select">
                ${tables.map(t => `<option value="${t.name}">${t.name}</option>`).join('')}
            </select>
        </label><div id="dynamic-fields"></div>`;

        // Append submit button (centered)
        form.innerHTML += `<div style="display:flex;justify-content:center;margin-top:28px;">
            <button type="submit" style="min-width:140px;">Submit</button>
        </div>`;

        // Append form to DOM before rendering fields!
        formContainer.appendChild(form);

        // Render fields for the first table by default
        renderTableFields(form, tables[0]);

        // Change fields on table select
        form.querySelector('#table-select').addEventListener('change', function () {
            const selected = tables.find(t => t.name === this.value);
            renderTableFields(form, selected);
        });
    } else if (forms[action.perm]) {
        renderFields(form, forms[action.perm]);
        // Center the submit button
        form.innerHTML += `<div style="display:flex;justify-content:center;margin-top:28px;">
            <button type="submit" style="min-width:140px;">Submit</button>
        </div>`;
        formContainer.appendChild(form);
    }

    form.onsubmit = async (e) => {
        e.preventDefault();
        let data;
        let api = action.api;

        if (action.perm === 'new_entry') {
            const tableName = form.elements['table'].value;
            const table = tables.find(t => t.name === tableName);
            if (tableName === 'Products') {
                data = new FormData();
                data.append('table', tableName);
                table.fields.forEach(field => {
                    if (field.type === 'file') {
                        data.append(field.name, form.elements[field.name].files[0]);
                    } else {
                        data.append(field.name, form.elements[field.name].value);
                    }
                });
            } else {
                data = { table: tableName };
                table.fields.forEach(field => {
                    data[field.name] = form.elements[field.name].value;
                });
            }
        } else {
            data = {};
            if (forms[action.perm]) {
                forms[action.perm].forEach(field => {
                    if (field.type === 'file') {
                        data[field.name] = form.elements[field.name].files[0];
                    } else {
                        data[field.name] = form.elements[field.name].value;
                    }
                });
            }
        }

        try {
            let res;
            if (action.perm === 'new_entry' && form.elements['table'].value === 'Products') {
                res = await fetch(api + '/Products', {
                    method: 'POST',
                    body: data
                });
            } else {
                res = await fetch(api, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
            }
            const result = await res.json();
            alert(result.message || 'Success');
        } catch (err) {
            alert('Error: ' + err.message);
        }
        formContainer.innerHTML = '';
    };
}