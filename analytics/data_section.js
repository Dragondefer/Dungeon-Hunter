document.addEventListener('DOMContentLoaded', () => {
    const dataTab = document.getElementById('data');
    if (!dataTab) return;

    // Data categories and subcategories with descriptions and sample stats
    const dataCategories = {
        Items: {
            description: "All types of items in the game.",
            subcategories: {
                Armor: {
                    description: "Protective gear that increases defense.",
                    stats: ["Defense", "Durability", "Weight"],
                    color: "#4ecdc4",
                    types: {
                        Gauntlets: { description: "Hand armor that increases strength and defense." },
                        Helmet: { description: "Head armor for protection." },
                        Chestplate: { description: "Torso armor for maximum protection." },
                        Leggings: { description: "Leg armor for mobility and defense." },
                        Boots: { description: "Footwear that enhances speed and defense." },
                        Shield: { description: "Defensive equipment to block attacks." }
                    }
                },
                Weapon: {
                    description: "Offensive gear that increases attack power.",
                    stats: ["Damage", "Attack Speed", "Range"],
                    color: "#ff6b6b",
                    types: {
                        Sword: { description: "Balanced melee weapon." },
                        Bow: { description: "Ranged weapon for attacking from a distance." },
                        Staff: { description: "Magical weapon for casting spells." },
                        Axe: { description: "Heavy weapon with high damage." },
                        Dagger: { description: "Fast, close-range weapon." },
                        Mace: { description: "Blunt weapon for crushing enemies." }
                    }
                },
                Ring: {
                    description: "Magical rings with various bonuses.",
                    stats: ["Bonus Effects", "Durability"],
                    color: "#ffd700",
                    types: {
                        GoldRing: { description: "Ring made of gold with magical properties." },
                        SilverRing: { description: "Ring made of silver with magical properties." }
                    }
                },
                Amulet: {
                    description: "Magical amulets with protective properties.",
                    stats: ["Bonus Effects", "Durability"],
                    color: "#667eea",
                    types: {
                        FireAmulet: { description: "Amulet that grants fire resistance." },
                        IceAmulet: { description: "Amulet that grants ice resistance." }
                    }
                },
                Belt: {
                    description: "Belts that enhance agility or stamina.",
                    stats: ["Agility Bonus", "Stamina Bonus"],
                    color: "#ff9f43",
                    types: {
                        LeatherBelt: { description: "Sturdy leather belt." },
                        ChainBelt: { description: "Chain belt with moderate protection." }
                    }
                }
            }
        },
        Enemies: {
            description: "All enemy types and bosses.",
            subcategories: {
                Normal: {
                    description: "Standard enemy types.",
                    stats: ["HP Modifier", "Attack Modifier", "Defense Modifier"],
                    types: {
                        Goblin: { description: "Small, weak enemy.", color: "#ff9999" },
                        Skeleton: { description: "Undead warrior.", color: "#cccccc" },
                        Wolf: { description: "Fast and agile predator.", color: "#996633" },
                        Orc: { description: "Strong and brutal fighter.", color: "#663300" },
                        Troll: { description: "Large and tough enemy.", color: "#336600" },
                        Ghost: { description: "Ethereal and elusive.", color: "#9999ff" },
                        DarkElf: { description: "Stealthy and deadly.", color: "#660066" },
                        Wraith: { description: "Fallen king's spirit.", color: "#333366" },
                        Golem: { description: "Stone guardian.", color: "#666666" },
                        Demon: { description: "Fiery and powerful.", color: "#cc3300" },
                        DragonWhelp: { description: "Young dragon.", color: "#ff6600" },
                        DarkShape: { description: "Shadowy figure.", color: "#000000" }
                    }
                },
                Bosses: {
                    description: "Powerful boss enemies.",
                    stats: ["HP Modifier", "Attack Modifier", "Defense Modifier", "Agility Modifier"],
                    types: {
                        GoblinKing: { description: "Leader of goblins.", color: "#ff6666" },
                        SkeletonLord: { description: "Undead commander.", color: "#999999" },
                        AlphaDireWolf: { description: "Pack leader wolf.", color: "#996633" },
                        OrcWarlord: { description: "Orcish war leader.", color: "#663300" },
                        AncientTroll: { description: "Elder troll.", color: "#336600" },
                        SpectreLord: { description: "Ghostly ruler.", color: "#9999ff" },
                        DarkElfQueen: { description: "Dark elf royalty.", color: "#660066" },
                        WraithKing: { description: "King of wraiths.", color: "#333366" },
                        AncientGolem: { description: "Ancient stone guardian.", color: "#666666" },
                        AncientDragon: { description: "Ancient dragon.", color: "#ff6600" },
                        DarkLord: { description: "Dark overlord.", color: "#000000" },
                        IronDragon: { description: "Iron scaled dragon.", color: "#999999" }
                    }
                }
            }
        },
        Skills: {
            description: "Character skills available in the game.",
            // color: "#ff6b6b",
            subcategories: {
                Melee: {
                    description: "Close combat skills.",
                    stats: ["Damage", "Stamina Cost", "Cooldown"],
                    color: "#ff2a2a",
                    types: {
                        Slash: { description: "A quick slashing attack." },
                        Bash: { description: "A heavy bash attack." },
                        Parry: { description: "Defensive skill to block attacks." }
                    }
                },
                Ranged: {
                    description: "Skills for ranged combat.",
                    stats: ["Damage", "Range", "Cooldown"],
                    color: "#3b5bdb",
                    types: {
                        Shoot: { description: "Basic ranged attack." },
                        Snipe: { description: "High damage long-range shot." },
                        Volley: { description: "Multiple arrows fired at once." }
                    }
                }
            }
        },
        Spells: {
            description: "Magical spells used by characters.",
            // color: "#667eea",
            subcategories: {
                Fire: {
                    description: "Fire-based spells.",
                    stats: ["Damage", "Mana Cost", "Cooldown"],
                    color: "#ff7f50",
                    types: {
                        Fireball: { description: "A ball of fire that explodes on impact." },
                        FlameWall: { description: "Creates a wall of fire." },
                        Ignite: { description: "Sets enemies on fire over time." }
                    }
                },
                Ice: {
                    description: "Ice-based spells.",
                    stats: ["Damage", "Mana Cost", "Cooldown"],
                    types: {
                        IceShard: { description: "Sharp shards of ice.", color: "#00bfff" },
                        FrostNova: { description: "Freezes enemies around the caster.", color: "#1e90ff" },
                        Blizzard: { description: "A storm of ice and snow.", color: "#87cefa" }
                    }
                }
            }
        },
        SpecialAttacks: {
            description: "Special attacks with unique effects.",
            color: "#ff9f43",
            subcategories: {
                PowerStrike: {
                    description: "A powerful melee attack.",
                    stats: ["Damage", "Stamina Cost", "Cooldown"],
                    types: {
                        HeavySmash: { description: "A heavy smash that stuns enemies.", color: "#ff9f43" },
                        Whirlwind: { description: "Spin attack hitting multiple enemies.", color: "#ffa726" }
                    }
                },
                MagicBurst: {
                    description: "Burst of magical energy.",
                    stats: ["Damage", "Mana Cost", "Cooldown"],
                    types: {
                        ArcaneBlast: { description: "A blast of arcane energy.", color: "#667eea" },
                        ShadowFlare: { description: "Dark energy explosion.", color: "#5c6bc0" }
                    }
                }
            }
        }
    };

    // Add styles for bubbles and detail view
    const style = document.createElement('style');
    style.textContent = `
        #data-bubbles-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 2rem;
            padding: 2rem;
        }
        .data-bubble {
            width: 180px;
            height: 120px;
            border-radius: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: transform 0.3s ease;
            user-select: none;
            padding: 1rem;
            text-align: center;
        }
        .data-bubble:hover {
            transform: scale(1.1);
        }
        #data-detail-view {
            padding: 1rem;
            color: white;
        }
        #data-detail-view h2 {
            margin-bottom: 0.5rem;
            color: #ffd700;
        }
        #data-detail-view h3 {
            margin-top: 1rem;
            margin-bottom: 0.3rem;
            color: #4ecdc4;
        }
        #data-detail-view ul {
            list-style-type: disc;
            margin-left: 1.5rem;
        }
        #data-detail-view button {
            margin: 1rem 0;
        }
    `;
    document.head.appendChild(style);

    // Create main bubbles container
    const bubblesContainer = document.createElement('div');
    bubblesContainer.id = 'data-bubbles-container';

    // Create detail view container (hidden initially)
    const detailView = document.createElement('div');
    detailView.id = 'data-detail-view';
    detailView.style.display = 'none';

    // Append containers to data tab
    dataTab.appendChild(bubblesContainer);
    dataTab.appendChild(detailView);

    // Function to create a bubble element with icon
    function createBubble(name, icon) {
        const bubble = document.createElement('div');
        bubble.className = 'data-bubble';

        const iconElem = document.createElement('div');
        iconElem.className = 'data-bubble-icon';
        iconElem.textContent = icon || '';
        bubble.appendChild(iconElem);

        const textElem = document.createElement('div');
        textElem.textContent = name;
        bubble.appendChild(textElem);

        return bubble;
    }

    // Function to show main bubbles
    function showMainBubbles() {
        detailView.style.display = 'none';
        bubblesContainer.style.display = 'flex';
        bubblesContainer.innerHTML = '';
        Object.entries(dataCategories).forEach(([category, data]) => {
            const bubble = createBubble(category, data.icon);
            bubble.addEventListener('click', () => {
                showCategoryDetails(category);
            });
            bubblesContainer.appendChild(bubble);
        });
    }

    // Function to show category details
    function showCategoryDetails(category) {
        bubblesContainer.style.display = 'none';
        detailView.style.display = 'block';
        detailView.innerHTML = '';

        const categoryData = dataCategories[category];
        const title = document.createElement('h2');
        title.textContent = category;
        detailView.appendChild(title);

        const description = document.createElement('p');
        description.textContent = categoryData.description;
        detailView.appendChild(description);

        // Back button
        const backButton = document.createElement('button');
        backButton.textContent = '← Back';
        backButton.className = 'btn btn-primary';
        backButton.addEventListener('click', () => {
            showMainBubbles();
        });
        detailView.appendChild(backButton);

        // Subcategories table
        if (Object.keys(categoryData.subcategories).length === 0) {
            const noSub = document.createElement('p');
            noSub.textContent = 'No subcategories available.';
            detailView.appendChild(noSub);
            return;
        }

        // If category is Items, add toolbar for filtering
        if (category === 'Items' || category === 'Skills' || category === 'Spells' || category === 'SpecialAttacks' || category === 'Enemies') {
            const toolbar = document.createElement('div');
            toolbar.style.marginBottom = '1rem';
            toolbar.style.display = 'flex';
            toolbar.style.flexWrap = 'wrap';
            toolbar.style.gap = '1rem';
            toolbar.style.alignItems = 'center';

            const label = document.createElement('span');
            label.textContent = 'Filter types:';
            label.style.fontWeight = 'bold';
            label.style.marginRight = '1rem';
            toolbar.appendChild(label);

            // Create checkboxes for each subcategory
            const checkboxes = {};
            Object.keys(categoryData.subcategories).forEach(subName => {
                const checkboxLabel = document.createElement('label');
                checkboxLabel.style.display = 'flex';
                checkboxLabel.style.alignItems = 'center';
                checkboxLabel.style.cursor = 'pointer';

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.checked = true;
                checkbox.style.marginRight = '0.3rem';
                checkbox.dataset.subName = subName;
                checkboxLabel.appendChild(checkbox);

                const colorSpan = document.createElement('span');
                colorSpan.textContent = subName;
                colorSpan.style.color = getColorForSubcategory(subName);
                checkboxLabel.appendChild(colorSpan);

                toolbar.appendChild(checkboxLabel);
                checkboxes[subName] = checkbox;
            });

            detailView.appendChild(toolbar);

            // Create table
            const table = document.createElement('table');
            table.style.width = '100%';
            table.style.borderCollapse = 'collapse';

            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            ['Name', 'Description', 'Stats/Effects', 'Formula'].forEach(text => {
                const th = document.createElement('th');
                th.textContent = text;
                th.style.border = '1px solid rgba(255, 255, 255, 0.3)';
                th.style.padding = '0.5rem';
                th.style.background = 'rgba(255, 215, 0, 0.3)';
                th.style.color = '#ffd700';
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);
            table.appendChild(thead);

            const tbody = document.createElement('tbody');
            Object.entries(categoryData.subcategories).forEach(([subName, subData]) => {
                if (subData.types) {
                    Object.entries(subData.types).forEach(([typeName, typeData]) => {
                        const tr = document.createElement('tr');
                        tr.dataset.subName = subName;
                        // Use subcategory color for all types within it
                        tr.style.backgroundColor = typeData.color || subData.color || 'transparent';
                        tr.style.border = '1px solid rgba(255, 255, 255, 0.3)';

                        const tdName = document.createElement('td');
                        tdName.textContent = typeName;
                        tdName.style.padding = '0.5rem';
                        tr.appendChild(tdName);

                        const tdDesc = document.createElement('td');
                        tdDesc.textContent = typeData.description;
                        tdDesc.style.padding = '0.5rem';
                        tr.appendChild(tdDesc);

                        const tdStats = document.createElement('td');
                        tdStats.textContent = subData.stats ? subData.stats.join(', ') : '';
                        tdStats.style.padding = '0.5rem';
                        tr.appendChild(tdStats);

                        const tdFormula = document.createElement('td');
                        tdFormula.textContent = subData.formula || '';
                        tdFormula.style.padding = '0.5rem';
                        tr.appendChild(tdFormula);

                        tbody.appendChild(tr);
                    });
                } else {
                    const tr = document.createElement('tr');
                    tr.dataset.subName = subName;
                    tr.style.color = getColorForSubcategory(subName);
                    tr.style.border = '1px solid rgba(255, 255, 255, 0.3)';

                    const tdName = document.createElement('td');
                    tdName.textContent = subName;
                    tdName.style.padding = '0.5rem';
                    tr.appendChild(tdName);

                    const tdDesc = document.createElement('td');
                    tdDesc.textContent = subData.description;
                    tdDesc.style.padding = '0.5rem';
                    tr.appendChild(tdDesc);

                    const tdStats = document.createElement('td');
                    tdStats.textContent = subData.stats ? subData.stats.join(', ') : '';
                    tdStats.style.padding = '0.5rem';
                    tr.appendChild(tdStats);

                    const tdFormula = document.createElement('td');
                    tdFormula.textContent = subData.formula || '';
                    tdFormula.style.padding = '0.5rem';
                    tr.appendChild(tdFormula);

                    tbody.appendChild(tr);
                }
            });
            table.appendChild(tbody);
            detailView.appendChild(table);

            // Add event listeners to checkboxes to filter table rows
            Object.values(checkboxes).forEach(checkbox => {
                checkbox.addEventListener('change', () => {
                    const checkedSubcategories = Object.entries(checkboxes)
                        .filter(([_, cb]) => cb.checked)
                        .map(([subName, _]) => subName);
                    Array.from(tbody.children).forEach(row => {
                        if (checkedSubcategories.includes(row.dataset.subName)) {
                            row.style.display = '';
                        } else {
                            row.style.display = 'none';
                        }
                    });
                });
            });

            return;
        }

        const table = document.createElement('table');
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        ['Name', 'Description', 'Stats/Effects', 'Formula'].forEach(text => {
            const th = document.createElement('th');
            th.textContent = text;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        const tbody = document.createElement('tbody');
        Object.entries(categoryData.subcategories).forEach(([subName, subData]) => {
            const tr = document.createElement('tr');

            const tdName = document.createElement('td');
            tdName.textContent = subName;
            tr.appendChild(tdName);

            const tdDesc = document.createElement('td');
            tdDesc.textContent = subData.description;
            tr.appendChild(tdDesc);

            const tdStats = document.createElement('td');
            tdStats.textContent = subData.stats ? subData.stats.join(', ') : '';
            tr.appendChild(tdStats);

            const tdFormula = document.createElement('td');
            tdFormula.textContent = subData.formula || '';
            tr.appendChild(tdFormula);

            tbody.appendChild(tr);
        });
        table.appendChild(tbody);
        detailView.appendChild(table);
    }

    // Helper function to get color for subcategory
    function getColorForSubcategory(subName) {
        const colors = {
            Armor: '#4ecdc4',
            Weapon: '#ff6b6b',
            Ring: '#ffd700',
            Amulet: '#667eea',
            Belt: '#ff9f43',
            Normal: '#ff6b6b',
            Bosses: '#ff9f43'
        };
        return colors[subName] || 'white';
    }

    // Initialize by showing main bubbles
    showMainBubbles();
});
